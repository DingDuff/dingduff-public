#!/usr/bin/env python3
"""Standalone review-bundle generator for DingDuff cite-check.

Reads cites.json (schema v1) plus the memo and source files it references,
verifies every file's checksum, pre-segments all documents (so the viewer's
JavaScript never performs offset arithmetic), and injects the payload into
the shared viewer template to produce a single self-contained review.html.

Checksum policy: any mismatch between cites.json and the bytes on disk is
fatal (exit 2) — wrong highlights are worse than no highlights. --force
proceeds, but suppresses highlights for mismatched documents and renders a
prominent warning banner.

Native rendering (cite-check 1.1): when cites.json records an `original`
binary for a source (sources/originals/*.pdf|docx), the bundle embeds the
file base64 plus the vendored viewer libraries it needs (PDF.js /
docx-preview — see viewer/vendor/MANIFEST.json), so the standalone panel
can show the source in native format with the same quote-anchored
highlights. Everything stays in this one local file — original documents
never leave the machine. The original-binary hash guards ONLY the native
render: a changed/oversized/missing original falls back to the verified
text view (recorded in payload.originals_skipped), never the other way
around. An original that fails its checksum is fatal without --force,
same policy as the text files.

Exit codes: 0 success; 2 fatal (missing/mismatched/unreadable files,
malformed cites.json, missing template placeholder, vendor-manifest drift).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from bisect import bisect_right
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_VERSION = "cite-check/build_review.py 1.1"
PAYLOAD_PLACEHOLDER = "/*__CITECHECK_PAYLOAD__*/"
VENDOR_PLACEHOLDER = "<!--__CITECHECK_VENDOR__-->"
SIZE_WARNING_CHARS = 15_000_000
HTML_SIZE_WARNING_CHARS = 50_000_000

# Per-file / total caps on embedded original binaries. Base64 adds ~33%, and
# the whole payload is parsed as one JSON string at load, so huge originals
# make the bundle sluggish or unopenable. Oversized files are skipped (text
# view still works) rather than fatal.
MAX_ORIGINAL_BYTES = 20_000_000
MAX_ORIGINALS_TOTAL_BYTES = 60_000_000

# LOCKSTEP with verify_anchors.py PAGE_MARKER_RE / the viewer's JS port —
# used here only to map anchor offsets to page numbers, never to rewrite text.
PAGE_MARKER_RE = re.compile(r"<<pg\. (\d+)>>")

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "viewer" / "review_viewer.html"

# Which vendored libraries each embeddable media type needs at view time.
# Only these media types have a native viewer; a text/plain original is
# provenance metadata in cites.json but embedding its bytes would be dead
# weight the panel never reads (transcript mode renders the extracted text).
MEDIA_VENDOR_FILES = {
    "application/pdf": ("pdfjs/pdf.min.mjs", "pdfjs/pdf.worker.min.mjs",
                        "pdfjs/text_layer.css"),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        ("jszip/jszip.min.js", "docx-preview/docx-preview.min.js"),
}

# DOM ids the viewer boots vendor code from (base64 in inert text/plain tags).
VENDOR_TAG_IDS = {
    "pdfjs/pdf.min.mjs": "cc-vendor-pdfjs",
    "pdfjs/pdf.worker.min.mjs": "cc-vendor-pdfjs-worker",
    "pdfjs/text_layer.css": "cc-vendor-pdfjs-css",
    "docx-preview/docx-preview.min.js": "cc-vendor-docx-preview",
    "jszip/jszip.min.js": "cc-vendor-jszip",
}


class FatalError(Exception):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_document(path: Path) -> str:
    # Decode failures become FatalError so the CLI honors its exit-2 contract
    # (a file can turn non-UTF-8 between verification and bundle time).
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FatalError(f"{path} is not valid UTF-8: {exc}") from exc


def binds_hash(cite_text: str, proposition: str) -> str:
    return hashlib.sha256(
        (cite_text + "\x00" + proposition).encode("utf-8")).hexdigest()


def segment_document(raw: str, spans: List[Tuple[int, int, str]]) -> List[Dict[str, Any]]:
    """Flatten (start, end, mark_id) spans into ordered segments whose text
    concatenation equals raw exactly. Overlapping spans compose: a segment
    carries every mark covering it."""
    clipped = [(max(0, s), min(len(raw), e), m) for s, e, m in spans if s < e]
    bounds = {0, len(raw)}
    for s, e, _ in clipped:
        bounds.add(s)
        bounds.add(e)
    ordered = sorted(bounds)
    segments: List[Dict[str, Any]] = []
    for a, b in zip(ordered, ordered[1:]):
        marks = [m for s, e, m in clipped if s <= a and b <= e]
        segments.append({"text": raw[a:b], "marks": marks})
    return segments


def escape_payload(payload: Dict[str, Any]) -> str:
    """JSON-encode the payload so it can never break out of its script tag:
    '<' becomes \\u003c (a legal JSON escape), so '</script>' and '<!--'
    cannot appear in the emitted HTML even if a source document contains
    them. U+2028/9 are escaped for safety in any inline-JS reuse."""
    text = json.dumps(payload, ensure_ascii=False)
    return (text.replace("<", "\\u003c")
                .replace("\u2028", "\\u2028")
                .replace("\u2029", "\\u2029"))


def load_cites(path: Path) -> Dict[str, Any]:
    try:
        cites = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FatalError(f"cannot read cites.json: {exc}") from exc
    if not isinstance(cites, dict) or cites.get("schema_version") != 1:
        raise FatalError("cites.json schema_version must be 1")
    for key in ("memo", "sources", "citations"):
        if key not in cites:
            raise FatalError(f"cites.json is missing '{key}'")
    return cites


def load_review(path: Path) -> Optional[Dict[str, Any]]:
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FatalError(f"cannot read review file: {exc}") from exc
    if not isinstance(review, dict) or review.get("schema_version") != 1:
        raise FatalError("review.json schema_version must be 1")
    return review


def anchor_pages_for(raw: str, spans: List[Tuple[int, int, str]]
                     ) -> Tuple[Optional[Dict[str, int]], Optional[int]]:
    """Map each anchor mark to the page whose `<<pg. N>>` marker most recently
    precedes its start offset. Computed here in Python because the offsets are
    Python codepoint indices — the viewer's JS must never do arithmetic on
    them. Returns (pages, first_page); first_page is the FIRST marker's
    printed number — mark_pdf_pages numbers pages contiguously from it, so
    the viewer maps a printed page N to PDF page ordinal N - first_page + 1
    (--first-page exhibits print 461-470 across physical pages 1-10).
    Returns (None, None) when the text carries no markers."""
    markers = [(m.start(), int(m.group(1))) for m in PAGE_MARKER_RE.finditer(raw)]
    if not markers:
        return None, None
    positions = [pos for pos, _ in markers]
    pages: Dict[str, int] = {}
    for start, _end, mark in spans:
        idx = bisect_right(positions, start) - 1
        if idx >= 0:
            pages[mark] = markers[idx][1]
    return pages, markers[0][1]


def embed_originals(cites: Dict[str, Any], workdir: Path
                    ) -> Tuple[Dict[str, Any], List[Dict[str, str]], List[str]]:
    """Load, verify, and base64 the original binaries recorded in cites.json.

    Returns (originals, skipped, checksum_failures). Missing, oversized, and
    non-renderable files are skipped with a recorded reason (the verified
    text view is unaffected); checksum failures are returned for the CALLER'S
    fatal-unless---force policy — this function only reports them.
    """
    originals: Dict[str, Any] = {}
    skipped: List[Dict[str, str]] = []
    checksum_failures: List[str] = []
    total = 0
    for key, src in cites["sources"].items():
        original = src.get("original")
        if not isinstance(original, dict) or not original.get("path"):
            continue
        if original.get("media_type") not in MEDIA_VENDOR_FILES:
            skipped.append({"key": key, "reason": "not_renderable"})
            continue
        path = workdir / original["path"]
        if not path.is_file():
            skipped.append({"key": key, "reason": "missing"})
            print(f"warning: original for {key} not found ({original['path']}); "
                  "the source will render as text only", file=sys.stderr)
            continue
        data = path.read_bytes()
        if original.get("sha256") and hashlib.sha256(data).hexdigest() != original["sha256"]:
            checksum_failures.append(original["path"])
            skipped.append({"key": key, "reason": "checksum_mismatch"})
            continue
        if len(data) > MAX_ORIGINAL_BYTES or total + len(data) > MAX_ORIGINALS_TOTAL_BYTES:
            skipped.append({"key": key, "reason": "too_large"})
            print(f"warning: original for {key} is too large to embed "
                  f"({len(data):,} bytes); the source will render as text only",
                  file=sys.stderr)
            continue
        total += len(data)
        entry: Dict[str, Any] = {
            "media_type": original["media_type"],
            "sha256": original.get("sha256"),
            "data_b64": base64.b64encode(data).decode("ascii"),
        }
        if isinstance(original.get("pages"), int):
            entry["pages"] = original["pages"]
        originals[key] = entry
    return originals, skipped, checksum_failures


def build_payload(cites: Dict[str, Any], workdir: Path, force: bool,
                  prior_review: Optional[Dict[str, Any]],
                  include_originals: bool = True) -> Tuple[Dict[str, Any], List[str]]:
    mismatches: List[str] = []
    total_chars = 0

    # --- memo ---
    memo_rel = cites["memo"]["path"]
    memo_path = workdir / memo_rel
    if not memo_path.is_file():
        raise FatalError(f"memo file not found: {memo_rel}")
    memo_ok = sha256_file(memo_path) == cites["memo"]["sha256"]
    if not memo_ok:
        mismatches.append(memo_rel)
    memo_raw = read_document(memo_path)
    total_chars += len(memo_raw)
    if memo_ok:
        memo_spans = [
            (c["memo_anchor"]["start"], c["memo_anchor"]["end"], c["id"])
            for c in cites["citations"] if c.get("memo_anchor")
        ]
        memo_doc = {"segments": segment_document(memo_raw, memo_spans),
                    "checksum_ok": True}
    else:
        memo_doc = {"segments": [{"text": memo_raw, "marks": []}],
                    "checksum_ok": False}

    # --- sources ---
    anchors_by_source: Dict[str, List[Tuple[int, int, str]]] = {}
    for c in cites["citations"]:
        for i, a in enumerate(c.get("anchors", [])):
            anchors_by_source.setdefault(c["source"], []).append(
                (a["start"], a["end"], f"{c['id']}:{i}"))

    source_docs: Dict[str, Any] = {}
    for key, src in cites["sources"].items():
        if src.get("missing") or not src.get("path"):
            source_docs[key] = {"segments": None, "checksum_ok": None, "missing": True}
            continue
        src_path = workdir / src["path"]
        if not src_path.is_file():
            raise FatalError(f"source file not found: {src['path']}")
        ok = sha256_file(src_path) == src["sha256"]
        if not ok:
            mismatches.append(src["path"])
        raw = read_document(src_path)
        total_chars += len(raw)
        if ok:
            spans = anchors_by_source.get(key, [])
            source_docs[key] = {
                "segments": segment_document(raw, spans),
                "checksum_ok": True,
            }
            pages, first_page = anchor_pages_for(raw, spans)
            if pages is not None:
                source_docs[key]["anchor_pages"] = pages
                source_docs[key]["first_page"] = first_page
        else:
            source_docs[key] = {"segments": [{"text": raw, "marks": []}],
                                "checksum_ok": False}

    if mismatches and not force:
        listing = "\n  ".join(mismatches)
        raise FatalError(
            "checksum mismatch — these files changed since cites.json was "
            f"generated:\n  {listing}\nRe-run /cite-check (or pass --force to "
            "render without highlights for the changed files).")

    # --- original binaries (native rendering; standalone bundle only) ---
    if include_originals:
        originals, originals_skipped, orig_checksum_failures = embed_originals(
            cites, workdir)
        if orig_checksum_failures and not force:
            listing = "\n  ".join(orig_checksum_failures)
            raise FatalError(
                "original document changed since cites.json was generated:\n  "
                f"{listing}\nA stale original would show the attorney the wrong "
                "page images. Re-run /cite-check (or pass --force to fall back "
                "to the verified text view for those sources).")
    else:
        originals = {}
        originals_skipped = [
            {"key": key, "reason": "disabled"}
            for key, src in cites["sources"].items()
            if isinstance(src.get("original"), dict)
        ]

    if total_chars > SIZE_WARNING_CHARS:
        print(f"warning: embedded documents total {total_chars:,} chars; "
              "review.html will be large", file=sys.stderr)

    binds = {c["id"]: c.get("binds_to") or binds_hash(c["cite_text"], c["proposition"])
             for c in cites["citations"]}

    payload = {
        "mode": "standalone",
        "generator": SCRIPT_VERSION,
        "cites": cites,
        "memo_doc": memo_doc,
        "source_docs": source_docs,
        "binds": binds,
        "prior_review": prior_review,
        "originals": originals,
        "originals_skipped": originals_skipped,
        "build": {"forced": bool(mismatches), "mismatches": mismatches},
    }
    return payload, mismatches


def load_vendor_manifest(vendor_dir: Path) -> Dict[str, Dict[str, Any]]:
    manifest_path = vendor_dir / "MANIFEST.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FatalError(f"cannot read vendor manifest {manifest_path}: {exc}") from exc
    return {lib["file"]: lib for lib in manifest.get("libraries", [])}


def render_vendor_block(payload: Dict[str, Any], vendor_dir: Path) -> str:
    """Base64 the vendored libraries the embedded originals need, as inert
    `<script type="text/plain">` tags the viewer boots via Blob URLs. Base64
    keeps the embedding HTML-safe (minified JS contains '</script>'-adjacent
    strings) and doubles as the Blob-worker source. Each file's sha256 is
    verified against MANIFEST.json — supply-chain drift is fatal, not silent.
    """
    needed: List[str] = []
    for entry in payload.get("originals", {}).values():
        for rel in MEDIA_VENDOR_FILES.get(entry["media_type"], ()):
            if rel not in needed:
                needed.append(rel)
    if not needed:
        return ""
    manifest = load_vendor_manifest(vendor_dir)
    tags: List[str] = []
    notices: List[str] = []
    for rel in needed:
        lib = manifest.get(rel)
        if lib is None:
            raise FatalError(f"vendor file {rel} is not in MANIFEST.json")
        path = vendor_dir / rel
        if not path.is_file():
            raise FatalError(f"vendor file not found: {path}")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != lib["sha256"]:
            raise FatalError(
                f"vendor file {rel} does not match MANIFEST.json "
                f"(expected {lib['sha256']}, got {digest}) — refusing to embed "
                "unverified third-party code")
        tags.append(f'<script type="text/plain" id="{VENDOR_TAG_IDS[rel]}">'
                    f'{base64.b64encode(data).decode("ascii")}</script>')
        notices.append(f"{lib['name']} {lib['version']} ({lib['license']})")
    header = ("<!-- Embedded third-party viewer libraries (offline native "
              "rendering): " + "; ".join(notices) +
              ". License texts: viewer/vendor/ in the dingduff-citation-check "
              "skill. -->")
    return header + "\n" + "\n".join(tags)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cites", required=True, help="path to cites.json")
    parser.add_argument("--out", required=True, help="path to write review.html")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE),
                        help="viewer template (defaults to the skill's shared viewer)")
    parser.add_argument("--review", default=None,
                        help="existing review.json to embed as prior verdicts")
    parser.add_argument("--workdir", default=".",
                        help="directory against which relative paths resolve")
    parser.add_argument("--force", action="store_true",
                        help="render despite checksum mismatches (highlights "
                             "suppressed for changed files; warning banner shown)")
    parser.add_argument("--no-originals", action="store_true",
                        help="text-only bundle: skip embedding original "
                             "PDF/DOCX binaries and their viewer libraries")
    args = parser.parse_args(argv)

    workdir = Path(args.workdir)
    try:
        template_path = Path(args.template)
        if not template_path.is_file():
            raise FatalError(f"viewer template not found: {args.template}")
        template = template_path.read_text(encoding="utf-8")
        if PAYLOAD_PLACEHOLDER not in template:
            raise FatalError("viewer template is missing the payload placeholder")

        cites = load_cites(workdir / args.cites)
        prior_review = load_review(workdir / args.review) if args.review else None
        payload, mismatches = build_payload(
            cites, workdir, args.force, prior_review,
            include_originals=not args.no_originals)
        vendor_block = render_vendor_block(payload, template_path.parent / "vendor")
        if vendor_block and VENDOR_PLACEHOLDER not in template:
            raise FatalError(
                "viewer template is missing the vendor placeholder "
                f"({VENDOR_PLACEHOLDER}) but the bundle embeds original "
                "documents — update the template or pass --no-originals")
    except FatalError as exc:
        print(f"fatal: {exc}", file=sys.stderr)
        return 2

    html = template.replace(PAYLOAD_PLACEHOLDER, escape_payload(payload), 1)
    html = html.replace(VENDOR_PLACEHOLDER, vendor_block, 1)
    if len(html) > HTML_SIZE_WARNING_CHARS:
        print(f"warning: review.html is {len(html):,} chars — large embedded "
              "originals make it slow to open; consider --no-originals",
              file=sys.stderr)
    out_path = workdir / args.out
    out_path.write_text(html, encoding="utf-8")
    if mismatches:
        print(f"wrote {args.out} WITH CHECKSUM WARNINGS: {', '.join(mismatches)}",
              file=sys.stderr)
    skipped = payload.get("originals_skipped") or []
    if skipped:
        print("originals not embedded: " +
              ", ".join(f"{s['key']} ({s['reason']})" for s in skipped),
              file=sys.stderr)
    print(json.dumps({"ok": True, "out": args.out,
                      "citations": len(cites["citations"]),
                      "originals_embedded": len(payload.get("originals") or {}),
                      "forced": bool(mismatches)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
