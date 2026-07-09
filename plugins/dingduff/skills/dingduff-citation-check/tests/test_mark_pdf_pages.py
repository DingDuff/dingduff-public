"""Tests for mark_pdf_pages.py — form-feed -> <<pg. N>> marker conversion."""

import json
import subprocess
import sys

import pytest


@pytest.fixture(scope="session")
def mp():
    from conftest import load_script
    return load_script("mark_pdf_pages")


class TestMarkPages:
    def test_basic_conversion(self, mp):
        marked, pages, empty = mp.mark_pages("first page\ftext of page two\f", 1)
        assert pages == 2 and empty == 0
        assert marked == "<<pg. 1>>\nfirst page<<pg. 2>>\ntext of page two"

    def test_first_page_offset(self, mp):
        marked, pages, _ = mp.mark_pages("a\fb", 17)
        assert "<<pg. 17>>" in marked and "<<pg. 18>>" in marked
        assert pages == 2

    def test_trailing_form_feed_not_a_phantom_page(self, mp):
        # pdftotext emits \f after the final page; that must not create an
        # empty trailing page (which would skew the scanned-PDF heuristic
        # and put a stray pill at the end of the document).
        _, pages, empty = mp.mark_pages("a\fb\f", 1)
        assert pages == 2 and empty == 0

    def test_interior_empty_pages_counted_and_kept(self, mp):
        marked, pages, empty = mp.mark_pages("a\f\fc", 1)
        assert pages == 3 and empty == 1
        # Page-count integrity: the empty page still gets its marker so
        # subsequent page numbers stay aligned with the PDF.
        assert "<<pg. 2>>" in marked and "<<pg. 3>>" in marked

    def test_double_marking_refused(self, mp):
        with pytest.raises(mp.FatalError):
            mp.mark_pages("already <<pg. 3>> marked\fmore", 1)

    def test_text_preserved_verbatim_between_markers(self, mp):
        body = "Line one.\n  Indented, hyphen-\nated line.\n"
        marked, _, _ = mp.mark_pages(body, 1)
        assert marked == "<<pg. 1>>\n" + body


class TestCLI:
    def _run(self, tmp_path, H, text, extra_args=None):
        src = tmp_path / "raw.txt"
        src.write_text(text, encoding="utf-8", newline="")
        out = tmp_path / "marked.md"
        cmd = [
            sys.executable, str(H.SCRIPTS_DIR / "mark_pdf_pages.py"),
            "--in", str(src), "--out", str(out),
        ] + (extra_args or [])
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc, out

    def test_happy_path_report(self, tmp_path, H):
        proc, out = self._run(tmp_path, H, "one\ftwo\fthree\f")
        assert proc.returncode == 0, proc.stderr
        report = json.loads(proc.stdout)
        assert report["ok"] is True and report["pages"] == 3
        assert out.read_text(encoding="utf-8").startswith("<<pg. 1>>\n")

    def test_first_page_flag(self, tmp_path, H):
        proc, out = self._run(tmp_path, H, "a\fb", ["--first-page", "461"])
        assert proc.returncode == 0
        text = out.read_text(encoding="utf-8")
        assert "<<pg. 461>>" in text and "<<pg. 462>>" in text

    def test_double_marking_exits_two(self, tmp_path, H):
        proc, out = self._run(tmp_path, H, "has <<pg. 9>> already")
        assert proc.returncode == 2
        assert "double-mark" in proc.stderr
        assert not out.exists()

    def test_scanned_pdf_warning(self, tmp_path, H):
        # 3 of 4 pages empty -> scanned-PDF heuristic fires on stderr.
        proc, _ = self._run(tmp_path, H, "text\f\f\f\f")
        assert proc.returncode == 0
        assert "scanned" in proc.stderr

    def test_no_form_feeds_warns(self, tmp_path, H):
        proc, _ = self._run(tmp_path, H, "just one big page of text")
        assert proc.returncode == 0
        assert "form feeds" in proc.stderr
        report = json.loads(proc.stdout)
        assert report["pages"] == 1

    def test_output_stable_for_verifier(self, tmp_path, H):
        # The marked file is what gets verified and hashed: same input must
        # yield byte-identical output across runs.
        proc1, out = self._run(tmp_path, H, "alpha\fbeta\f")
        first = out.read_bytes()
        proc2, out = self._run(tmp_path, H, "alpha\fbeta\f")
        assert out.read_bytes() == first
