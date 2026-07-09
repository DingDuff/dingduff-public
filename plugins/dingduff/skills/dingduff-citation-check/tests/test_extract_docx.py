"""Tests for extract_docx.py — the .docx -> Markdown front-end for cite-check.

The invariants that matter for citation integrity: footnoted cites survive,
tracked deletions do not leak into the checked text, and the same .docx always
produces byte-identical Markdown (so the memo SHA-256 is stable).
"""

import subprocess
import sys

import pytest

from conftest import SCRIPTS_DIR, make_docx


def _memo_docx(path):
    """A realistic memo: heading, body cite, a footnoted cite, a tracked edit."""
    return make_docx(
        path,
        paragraphs=[
            {"style": "Heading1", "runs": [("t", "Memorandum: Limitations")]},
            {"runs": [
                ("t", "The discovery rule controls. "),
                ("t", "Smith v. Jones, 123 F.3d 456, 461 (9th Cir. 1997)."),
                ("foot", "1"),
            ]},
            {"runs": [
                ("ins", "The clock starts at discovery. "),
                ("del", "The clock starts at filing. "),
                ("t", "Final sentence."),
            ]},
        ],
        footnotes=[("1", "See Doe v. Roe, 200 F.3d 100, 105 (9th Cir. 2000).")],
    )


class TestExtract:
    def test_body_order_and_heading(self, ed, tmp_path):
        md, report = ed.extract_docx(_memo_docx(tmp_path / "memo.docx"))
        assert "# Memorandum: Limitations" in md
        assert "The discovery rule controls. Smith v. Jones, 123 F.3d 456, 461 (9th Cir. 1997).[^1]" in md
        # body precedes the footnotes section
        assert md.index("Final sentence.") < md.index("## Footnotes")

    def test_footnote_citation_survives(self, ed, tmp_path):
        md, report = ed.extract_docx(_memo_docx(tmp_path / "memo.docx"))
        assert "## Footnotes" in md
        assert "[^1]: See Doe v. Roe, 200 F.3d 100, 105 (9th Cir. 2000)." in md
        assert report["footnotes"] == 1

    def test_separator_footnotes_excluded(self, ed, tmp_path):
        # ids -1 and 0 are Word's separator glyphs and must not appear as notes.
        md, report = ed.extract_docx(_memo_docx(tmp_path / "memo.docx"))
        assert "[^-1]" not in md and "[^0]:" not in md
        assert report["footnotes"] == 1

    def test_orphan_note_definitions_excluded(self, ed, tmp_path):
        # A footnote DEFINITION with no matching reference in the body (e.g. its
        # reference was deleted via tracked changes) must not leak into the text.
        p = make_docx(
            tmp_path / "orphan.docx",
            paragraphs=[{"runs": [("t", "Body with one ref."), ("foot", "1")]}],
            footnotes=[("1", "Referenced footnote, 1 U.S. 1."),
                       ("2", "ORPHAN footnote, 999 U.S. 999.")],
        )
        md, report = ed.extract_docx(p)
        assert "Referenced footnote, 1 U.S. 1." in md
        assert "ORPHAN" not in md
        assert report["footnotes"] == 1

    def test_tracked_changes_accept_all_view(self, ed, tmp_path):
        md, report = ed.extract_docx(_memo_docx(tmp_path / "memo.docx"))
        assert "The clock starts at discovery." in md   # inserted -> kept
        assert "The clock starts at filing." not in md  # deleted -> dropped
        assert report["has_tracked_changes"] is True
        assert report["tracked_insertions"] == 1
        assert report["tracked_deletions"] == 1

    def test_endnotes_section(self, ed, tmp_path):
        p = make_docx(
            tmp_path / "e.docx",
            paragraphs=[{"runs": [("t", "Body text."), ("end", "1")]}],
            endnotes=[("1", "Endnote authority, 1 U.S. 1 (1900).")],
        )
        md, report = ed.extract_docx(p)
        assert "Body text.[^e1]" in md
        assert "## Endnotes" in md
        assert "[^e1]: Endnote authority, 1 U.S. 1 (1900)." in md
        assert report["endnotes"] == 1

    def test_deterministic_byte_stable(self, ed, tmp_path):
        a, _ = ed.extract_docx(_memo_docx(tmp_path / "a.docx"))
        b, _ = ed.extract_docx(_memo_docx(tmp_path / "b.docx"))
        assert a == b
        assert a.encode("utf-8").decode("utf-8") == a  # valid UTF-8

    def test_no_tracked_changes_flag_clean_doc(self, ed, tmp_path):
        p = make_docx(tmp_path / "c.docx",
                      paragraphs=[{"runs": [("t", "Just plain text.")]}])
        md, report = ed.extract_docx(p)
        assert report["has_tracked_changes"] is False

    def test_table_cells_captured(self, ed, tmp_path):
        # Build a doc with a table by hand (make_docx only does paragraphs).
        from conftest import W_NS
        import zipfile
        doc = (f'<?xml version="1.0"?><w:document xmlns:w="{W_NS}"><w:body>'
               '<w:tbl><w:tr>'
               '<w:tc><w:p><w:r><w:t>Claim One</w:t></w:r></w:p></w:tc>'
               '<w:tc><w:p><w:r><w:t>Roe v. Wade, 410 U.S. 113</w:t></w:r></w:p></w:tc>'
               '</w:tr></w:tbl></w:body></w:document>')
        p = tmp_path / "t.docx"
        with zipfile.ZipFile(p, "w") as zf:
            zf.writestr("word/document.xml", doc)
        md, _ = ed.extract_docx(p)
        assert "Claim One | Roe v. Wade, 410 U.S. 113" in md

    def test_not_a_docx_is_fatal(self, ed, tmp_path):
        bad = tmp_path / "not.docx"
        bad.write_text("plain text, not a zip", encoding="utf-8")
        with pytest.raises(ed.FatalError):
            ed.extract_docx(bad)


class TestCli:
    def test_cli_writes_and_reports(self, tmp_path):
        src = _memo_docx(tmp_path / "memo.docx")
        out = tmp_path / "memo.md"
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "extract_docx.py"),
             "--in", str(src), "--out", str(out)],
            capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        import json
        report = json.loads(proc.stdout)
        assert report["ok"] and report["footnotes"] == 1
        assert out.read_text(encoding="utf-8").startswith("# Memorandum")
        # tracked-change warning goes to stderr, not stdout
        assert "tracked changes" in proc.stderr


class TestEndToEnd:
    def test_extracted_memo_anchors_through_verifier(self, ed, tmp_path, H):
        """Convert a .docx memo, then cite-check it against a stored opinion."""
        memo_docx = make_docx(
            tmp_path / "brief.docx",
            paragraphs=[{"runs": [
                ("t", "The discovery rule controls. "),
                ("t", "Smith v. Jones, 123 F.3d 456, 461 (9th Cir. 1997)."),
            ]}],
        )
        md, _ = ed.extract_docx(memo_docx)
        (tmp_path / "memo.md").write_text(md, encoding="utf-8")
        (tmp_path / "sources").mkdir()
        (tmp_path / "sources" / "smith_v_jones_12345.md").write_text(
            H.make_opinion_md(), encoding="utf-8")

        proposals = H.base_proposals(
            [H.citation(
                cite_text="Smith v. Jones, 123 F.3d 456, 461 (9th Cir. 1997)",
                proposition="The discovery rule governs accrual.",
                quotes=["The limitations period does not begin to run until "
                        "the plaintiff knows or has reason to know of the injury"],
            )],
            sources={"cl-12345": {
                "type": "opinion",
                "path": "sources/smith_v_jones_12345.md",
                "cluster_id": "12345",
                "case_name": "Smith v. Jones",
                "citation": "123 F.3d 456",
            }},
        )
        code, report, cites, stderr = H.run_cli(tmp_path, proposals)
        assert code == 0, stderr
        assert cites["citations"][0]["status"] == "anchored"
        H.assert_anchor_invariant(tmp_path, cites)
