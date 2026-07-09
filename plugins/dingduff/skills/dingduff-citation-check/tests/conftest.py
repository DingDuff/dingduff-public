"""Shared fixtures for cite-check skill tests.

The skill's scripts are standalone files (not a package), so they are loaded
via importlib straight from skills/cite-check/scripts/.
"""

import importlib.util
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import pytest

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
SCHEMAS_DIR = SKILL_DIR / "schemas"
VECTORS_PATH = Path(__file__).resolve().parent / "normalization_vectors.json"


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolve annotations via sys.modules
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def va():
    """The verify_anchors module."""
    return load_script("verify_anchors")


@pytest.fixture(scope="session")
def ed():
    """The extract_docx module."""
    return load_script("extract_docx")


@pytest.fixture(scope="session")
def vectors():
    return json.loads(VECTORS_PATH.read_text(encoding="utf-8"))["vectors"]


# ---------------------------------------------------------------------------
# Minimal .docx builder — enough OOXML for extract_docx (which reads only
# word/document.xml + word/footnotes.xml + word/endnotes.xml directly).
# ---------------------------------------------------------------------------

def _docx_paragraph(runs, style=None):
    """runs: list of (kind, value). kinds: 't','ins','del','foot','end','tab','br'."""
    ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    parts = []
    for kind, val in runs:
        if kind == "t":
            parts.append(f'<w:r><w:t xml:space="preserve">{escape(val)}</w:t></w:r>')
        elif kind == "ins":
            parts.append('<w:ins><w:r><w:t xml:space="preserve">'
                         f'{escape(val)}</w:t></w:r></w:ins>')
        elif kind == "del":
            parts.append('<w:del><w:r><w:delText xml:space="preserve">'
                         f'{escape(val)}</w:delText></w:r></w:del>')
        elif kind == "foot":
            parts.append(f'<w:r><w:footnoteReference w:id="{val}"/></w:r>')
        elif kind == "end":
            parts.append(f'<w:r><w:endnoteReference w:id="{val}"/></w:r>')
        elif kind == "tab":
            parts.append("<w:r><w:tab/></w:r>")
        elif kind == "br":
            parts.append("<w:r><w:br/></w:r>")
    return f"<w:p>{ppr}{''.join(parts)}</w:p>"


def _docx_notes_xml(container, item, notes):
    seps = (
        f'<w:{item} w:type="separator" w:id="-1"><w:p><w:r><w:t></w:t></w:r></w:p></w:{item}>'
        f'<w:{item} w:type="continuationSeparator" w:id="0"><w:p><w:r><w:t></w:t></w:r></w:p></w:{item}>'
    )
    body = "".join(
        f'<w:{item} w:id="{nid}"><w:p><w:r><w:t xml:space="preserve">'
        f'{escape(text)}</w:t></w:r></w:p></w:{item}>'
        for nid, text in notes
    )
    return f'<w:{container} xmlns:w="{W_NS}">{seps}{body}</w:{container}>'


def make_docx(path, paragraphs, footnotes=None, endnotes=None):
    """Write a minimal .docx. paragraphs: list of {'runs': [...], 'style': str?}."""
    body = "".join(_docx_paragraph(p["runs"], p.get("style")) for p in paragraphs)
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:document xmlns:w="{W_NS}"><w:body>{body}<w:sectPr/></w:body></w:document>')
    parts = {"word/document.xml": document}
    if footnotes:
        parts["word/footnotes.xml"] = _docx_notes_xml("footnotes", "footnote", footnotes)
    if endnotes:
        parts["word/endnotes.xml"] = _docx_notes_xml("endnotes", "endnote", endnotes)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in parts.items():
            zf.writestr(name, content)
    return path


# ---------------------------------------------------------------------------
# Fixture document builders — mirror opinion_store / statute_store output
# ---------------------------------------------------------------------------

DEFAULT_OPINION_BODY = (
    "The “totality of the circumstances” governs our review. We have "
    "long held that a plaintiff must demonstrate a reasonable expecta-\ntion of "
    "privacy in the place searched. The limitations period does not begin to "
    "run until the plaintiff knows or has reason to know of the injury that "
    "forms the basis of the action. This principle—deeply rooted in our "
    "precedent—admits of no exception. A well-\nknown corollary follows "
    "from that rule. Damages are unavailable… absent proof of actual harm "
    "to the claimant."
)


def make_opinion_md(
    body: str = DEFAULT_OPINION_BODY,
    case_name: str = "Smith v. Jones",
    cluster_id: str = "12345",
    citation: str = "123 F.3d 456",
    dissent: str = "",
    citing_snippet: str = "an unrelated snippet about procedure",
) -> str:
    parts = [
        "Case file generated by DingDuff using data from CourtListener:",
        "",
        f"# {case_name}",
        "",
        f"**Cluster ID:** {cluster_id}",
        "**Court:** United States Court of Appeals for the Ninth Circuit (ca9)",
        "**Date Filed:** 1997-03-15",
        "**Precedential Status:** Published",
        f"**Citations:** {citation}",
        "",
        "---",
        "",
        "## Lead Opinion — Trott",
        "",
        body,
    ]
    if dissent:
        parts += ["", "---", "", "## Dissenting Opinion — Kozinski", "", dissent]
    parts += [
        "",
        "---",
        "",
        "## Citing Cases (1)",
        "",
        "Showing the 1 most recent of 1 citing cases.",
        "",
        f"1. **Doe v. Roe** 200 F.3d 100, 2005 — cluster 99999 • ca9",
        f"   > {citing_snippet}",
        "",
        "---",
        "",
        f"*Generated by DingDuff at 2026-06-11T12:00:00Z. Source: CourtListener "
        f"cluster {cluster_id}.*",
    ]
    return "\n".join(parts)


def make_statute_md(
    text: str = (
        "A landlord shall install a smoke alarm in each bedroom of a dwelling "
        "unit. The landlord shall test each smoke alarm at the beginning of "
        "the tenant's possession."
    ),
    citation: str = "Tex. Prop. Code § 92.006",
    section: str = "92.006",
) -> str:
    return "\n".join([
        f"# {citation}",
        "## Smoke Alarms",
        "",
        "**Jurisdiction:** Texas (TX)",
        "**Code:** Property Code",
        f"**Section:** {section}",
        "**Effective Date:** 2010-01-01",
        "",
        text,
    ])


DEFAULT_MEMO = (
    "# Memorandum: Statute of Limitations\n"
    "\n"
    "The discovery rule controls. Smith v. Jones, 123 F.3d 456, 461 "
    "(9th Cir. 1997). Under that rule, the limitations clock starts only at "
    "discovery of the injury. Id. at 462. A plaintiff must also demonstrate "
    "a reasonable expectation of privacy in the place searched. Id. at 463. "
    "Texas law independently requires smoke alarms in each bedroom. "
    "Tex. Prop. Code § 92.006.\n"
)


def write_project(tmp_path: Path, memo: str = DEFAULT_MEMO, sources: dict = None):
    """Write a mini project folder; returns dict of relative paths.

    sources: {relative_path: content}; defaults to one opinion + one statute.
    """
    if sources is None:
        sources = {
            "sources/smith_v_jones_12345.md": make_opinion_md(),
            "sources/tex_prop_code_92_006.md": make_statute_md(),
        }
    (tmp_path / "memo.md").write_text(memo, encoding="utf-8")
    for rel, content in sources.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return {"memo": "memo.md", "sources": list(sources)}


def base_proposals(citations: list, sources: dict = None) -> dict:
    if sources is None:
        sources = {
            "cl-12345": {
                "type": "opinion",
                "path": "sources/smith_v_jones_12345.md",
                "cluster_id": "12345",
                "case_name": "Smith v. Jones",
                "citation": "123 F.3d 456",
            },
            "stat-tex_prop_code_92_006": {
                "type": "statute",
                "path": "sources/tex_prop_code_92_006.md",
                "statute_id": "TX/property/92.006",
                "code": "Property Code",
                "section": "92.006",
            },
        }
    return {
        "schema_version": 1,
        "memo": {"path": "memo.md"},
        "sources": sources,
        "citations": citations,
    }


def citation(cid="c001", source="cl-12345", cite_text="Smith v. Jones, 123 F.3d 456, 461 (9th Cir. 1997)",
             proposition="The discovery rule applies.", quotes=None, **extra):
    entry = {
        "id": cid,
        "source": source,
        "cite_text": cite_text,
        "proposition": proposition,
        "support_type": extra.pop("support_type", "paraphrase"),
        "anchors_proposed": [{"quote": q} for q in (quotes or [])],
    }
    entry.update(extra)
    return entry


def run_cli(workdir: Path, proposals: dict, extra_args: list = None):
    """Run verify_anchors.py as a subprocess; returns (exit_code, report, cites)."""
    scratch = workdir / ".cite-check"
    scratch.mkdir(exist_ok=True)
    (scratch / "proposals.json").write_text(
        json.dumps(proposals, ensure_ascii=False), encoding="utf-8")
    cmd = [
        sys.executable, str(SCRIPTS_DIR / "verify_anchors.py"),
        "--proposals", ".cite-check/proposals.json",
        "--out", "cites.json",
        "--workdir", str(workdir),
    ] + (extra_args or [])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    report = json.loads(proc.stdout) if proc.returncode in (0, 1) and proc.stdout else None
    cites_path = workdir / "cites.json"
    cites = (json.loads(cites_path.read_text(encoding="utf-8"))
             if cites_path.is_file() else None)
    return proc.returncode, report, cites, proc.stderr


def run_build(workdir: Path, extra_args: list = None):
    """Run build_review.py as a subprocess; returns (exit_code, stdout, stderr)."""
    cmd = [
        sys.executable, str(SCRIPTS_DIR / "build_review.py"),
        "--cites", "cites.json",
        "--out", "review.html",
        "--workdir", str(workdir),
    ] + (extra_args or [])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


PAYLOAD_TAG = '<script id="citecheck-payload" type="application/json">'


def extract_payload(html: str) -> dict:
    """Pull the embedded JSON payload back out of a generated review.html."""
    start = html.index(PAYLOAD_TAG) + len(PAYLOAD_TAG)
    end = html.index("</script>", start)
    return json.loads(html[start:end])


@pytest.fixture(scope="session")
def H():
    """Helper namespace — avoids importing conftest by module name, which is
    unreliable when multiple test directories are collected together."""
    import types
    return types.SimpleNamespace(
        SKILL_DIR=SKILL_DIR,
        SCRIPTS_DIR=SCRIPTS_DIR,
        SCHEMAS_DIR=SCHEMAS_DIR,
        DEFAULT_OPINION_BODY=DEFAULT_OPINION_BODY,
        DEFAULT_MEMO=DEFAULT_MEMO,
        make_opinion_md=make_opinion_md,
        make_statute_md=make_statute_md,
        write_project=write_project,
        base_proposals=base_proposals,
        citation=citation,
        make_docx=make_docx,
        run_cli=run_cli,
        run_build=run_build,
        extract_payload=extract_payload,
        PAYLOAD_TAG=PAYLOAD_TAG,
        assert_anchor_invariant=assert_anchor_invariant,
    )


def assert_anchor_invariant(workdir: Path, cites: dict):
    """Every anchor's quote must equal the raw slice of its source file, and
    every memo_anchor must slice to its cite_text (normalized-equal)."""
    raw_cache = {}

    def raw_of(rel):
        if rel not in raw_cache:
            raw_cache[rel] = (workdir / rel).read_bytes().decode("utf-8")
        return raw_cache[rel]

    for cit in cites["citations"]:
        src = cites["sources"][cit["source"]]
        for anchor in cit["anchors"]:
            raw = raw_of(src["path"])
            assert raw[anchor["start"]:anchor["end"]] == anchor["quote"], (
                f"{cit['id']}: anchor slice mismatch")
        if cit["memo_anchor"]:
            raw = raw_of(cites["memo"]["path"])
            sliced = raw[cit["memo_anchor"]["start"]:cit["memo_anchor"]["end"]]
            assert sliced, f"{cit['id']}: empty memo anchor slice"
