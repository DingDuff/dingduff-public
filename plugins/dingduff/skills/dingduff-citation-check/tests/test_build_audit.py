"""Tests for build_audit.py — the printable attorney audit log."""

import json
import subprocess
import sys

import pytest


@pytest.fixture(scope="session")
def ba():
    from conftest import load_script
    return load_script("build_audit")


def _project_with_cites(tmp_path, H, extra_citations=None):
    H.write_project(tmp_path)
    citations = [
        H.citation("c001", quotes=[
            'The "totality of the circumstances" governs our review.']),
        H.citation("c002", source="stat-tex_prop_code_92_006",
                   cite_text="Tex. Prop. Code § 92.006",
                   proposition="Smoke alarms are required.",
                   quotes=["A landlord shall install a smoke alarm in each bedroom"]),
        H.citation("c003", cite_text="Id. at 463.",
                   memo_context="privacy in the place searched. Id. at 463.",
                   proposition="A fabricated proposition.",
                   quotes=["this passage does not exist in the opinion"]),
    ] + (extra_citations or [])
    code, report, cites, err = H.run_cli(tmp_path, H.base_proposals(citations))
    assert code in (0, 1), err
    return cites


def _write_review(tmp_path, ba, cites, entries):
    reviews = {}
    for cid, verdict, note in entries:
        c = next(x for x in cites["citations"] if x["id"] == cid)
        reviews[cid] = {"verdict": verdict, "note": note, "reviewer": "KD",
                        "at": "2026-06-12T00:00:00Z", "binds_to": c["binds_to"]}
    (tmp_path / "review.json").write_text(
        json.dumps({"schema_version": 1, "reviews": reviews}), encoding="utf-8")


def _run_audit(tmp_path, with_review=True, extra=None):
    cmd = [sys.executable,
           str((tmp_path / "..").resolve())]  # placeholder, replaced below
    from conftest import SCRIPTS_DIR
    cmd = [sys.executable, str(SCRIPTS_DIR / "build_audit.py"),
           "--cites", "cites.json", "--out", "audit.html",
           "--workdir", str(tmp_path)] + (
        ["--review", "review.json"] if with_review else []) + (extra or [])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    html = (tmp_path / "audit.html").read_text(encoding="utf-8") \
        if (tmp_path / "audit.html").exists() else ""
    return proc.returncode, html, proc.stderr


class TestAuditLog:
    def test_emoji_mapping_and_columns(self, tmp_path, H, ba):
        cites = _project_with_cites(tmp_path, H)
        _write_review(tmp_path, ba, cites, [
            ("c001", "verified", ""),
            ("c002", "needs_attention", "statute cite is to subsection (a) only"),
        ])
        code, html, err = _run_audit(tmp_path)
        assert code == 0, err
        # One row per citation; statuses: ✅ ⚠️ and ❓ for unreviewed c003.
        assert html.count("<tr>") == 1 + 3  # thead + 3 body rows
        assert "✅" in html and "⚠️" in html and "❓" in html
        assert "statute cite is to subsection (a) only" in html
        assert "KD" in html
        # All seven headers present.
        for col in ("#", "Source cited", "Proposition cited for", "Anchored?",
                    "Review", "Review note", "Reviewed by"):
            assert col in html
        # Anchored column distinguishes verifier outcomes.
        assert "✓ Verbatim" in html
        assert "✗ not found" in html  # c003's fabricated quote

    def test_landscape_print_css(self, tmp_path, H):
        _project_with_cites(tmp_path, H)
        code, html, err = _run_audit(tmp_path, with_review=False)
        assert code == 0, err
        assert "size: letter landscape" in html
        assert "table-header-group" in html  # headers repeat per printed page

    def test_missing_review_means_all_unreviewed(self, tmp_path, H):
        _project_with_cites(tmp_path, H)
        code, html, err = _run_audit(tmp_path, with_review=False)
        assert code == 0, err
        assert html.count("❓") >= 3
        assert "0/3 citations attorney-reviewed" in html

    def test_legacy_verdicts_mapped(self, tmp_path, H, ba):
        cites = _project_with_cites(tmp_path, H)
        _write_review(tmp_path, ba, cites, [
            ("c001", "misquoted", "quote altered"),
            ("c002", "wrong_pin", ""),
        ])
        code, html, err = _run_audit(tmp_path)
        assert code == 0, err
        assert "‼️" in html and "⚠️" in html
        assert "[recorded as misquoted]" in html
        assert "[recorded as wrong_pin]" in html

    def test_stale_review_excluded_from_stdout_count(self, tmp_path, H, ba):
        """The JSON summary's `reviewed` must share the table's semantics:
        stale entries are NOT attorney-reviewed (Copilot review of #225)."""
        import subprocess, sys as _sys, json as _json
        from conftest import SCRIPTS_DIR
        cites = _project_with_cites(tmp_path, H)
        _write_review(tmp_path, ba, cites, [("c001", "verified", "")])
        review = _json.loads((tmp_path / "review.json").read_text())
        review["reviews"]["c001"]["binds_to"] = "f" * 64  # stale
        (tmp_path / "review.json").write_text(_json.dumps(review), encoding="utf-8")
        proc = subprocess.run(
            [_sys.executable, str(SCRIPTS_DIR / "build_audit.py"),
             "--cites", "cites.json", "--review", "review.json",
             "--out", "audit.html", "--workdir", str(tmp_path)],
            capture_output=True, text=True)
        assert proc.returncode == 0
        assert _json.loads(proc.stdout)["reviewed"] == 0

    def test_stale_review_not_applied(self, tmp_path, H, ba):
        cites = _project_with_cites(tmp_path, H)
        _write_review(tmp_path, ba, cites, [("c001", "verified", "")])
        # Tamper the stored binds_to so the verdict no longer matches.
        review = json.loads((tmp_path / "review.json").read_text())
        review["reviews"]["c001"]["binds_to"] = "f" * 64
        (tmp_path / "review.json").write_text(json.dumps(review), encoding="utf-8")
        code, html, err = _run_audit(tmp_path)
        assert code == 0, err
        assert "earlier version of this citation" in html
        # The stale verified verdict must not appear as a live status cell
        # (✅ still legitimately appears in the legend and zero-counts).
        assert '<td class="status">✅</td>' not in html
        assert "✅ 0" in html

    def test_notes_are_escaped(self, tmp_path, H, ba):
        cites = _project_with_cites(tmp_path, H)
        evil = '</td></tr></table><script>alert(1)</script>'
        _write_review(tmp_path, ba, cites, [("c001", "rejected", evil)])
        code, html, err = _run_audit(tmp_path)
        assert code == 0, err
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html

    def test_brand_mark_is_inline_svg_not_data_image(self, tmp_path, H):
        # The dog MUST be inline SVG, never a data: <img> — MCP App iframes and
        # some print/preview contexts block data: images via CSP (img-src).
        _project_with_cites(tmp_path, H)
        code, html, err = _run_audit(tmp_path, with_review=False)
        assert code == 0, err
        assert "data:image" not in html
        assert "<svg" in html and "<rect" in html
        assert "DingDuff Citation Verification Audit Log" in html

    def test_integrity_footer(self, tmp_path, H):
        cites = _project_with_cites(tmp_path, H)
        code, html, err = _run_audit(tmp_path, with_review=False)
        assert code == 0, err
        assert cites["memo"]["sha256"] in html
        assert "Integrity record" in html
        assert "build_audit.py" in html

    def test_malformed_cites_exit_two(self, tmp_path, H):
        (tmp_path / "cites.json").write_text('{"schema_version": 9}', encoding="utf-8")
        code, html, err = _run_audit(tmp_path, with_review=False)
        assert code == 2 and "schema_version" in err

    def test_unit_helpers(self, ba):
        assert ba.source_label({"type": "opinion", "case_name": "A v. B",
                                "citation": "1 U.S. 1"}) == "A v. B, 1 U.S. 1"
        assert ba.source_label({"type": "statute", "code": "Property Code",
                                "section": "92.006"}) == "Property Code § 92.006"
        assert ba.source_label({"type": "document", "title": "Defendant's MSJ Brief",
                                "kind": "brief"}) == "Defendant's MSJ Brief (brief)"
        assert ba.source_label({"type": "document"}) == "supplied document"
        assert ba.anchored_label({"status": "anchored",
                                  "anchors": [{"match": "exact"}]}) == "✓ Verbatim"
        assert ba.anchored_label({"status": "anchored",
                                  "anchors": [{"match": "exact"}, {"match": "normalized"}]}
                                 ) == "✓ Verbatim (formatting differs)"
        assert ba.anchored_label({"status": "anchor_failed",
                                  "failure_reason": "source_missing"}) == "— source missing"
