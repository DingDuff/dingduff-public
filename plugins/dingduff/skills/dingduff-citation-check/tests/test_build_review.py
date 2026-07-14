"""Tests for build_review.py — the standalone review-bundle generator."""

import hashlib
import json

import pytest


@pytest.fixture(scope="session")
def br():
    from conftest import load_script
    return load_script("build_review")


def _verified_project(tmp_path, H, extra_citations=None, citing_snippet=None):
    """Build a project, run the verifier, return (report, cites)."""
    kwargs = {}
    if citing_snippet is not None:
        kwargs["sources"] = {
            "sources/smith_v_jones_12345.md": H.make_opinion_md(citing_snippet=citing_snippet),
            "sources/tex_prop_code_92_006.md": H.make_statute_md(),
        }
    H.write_project(tmp_path, **kwargs)
    citations = [
        H.citation("c001", quotes=[
            'The "totality of the circumstances" governs our review.']),
        H.citation("c002", source="stat-tex_prop_code_92_006",
                   cite_text="Tex. Prop. Code § 92.006",
                   proposition="Smoke alarms are required in bedrooms.",
                   quotes=["A landlord shall install a smoke alarm in each bedroom"]),
    ] + (extra_citations or [])
    code, report, cites, err = H.run_cli(tmp_path, H.base_proposals(citations))
    assert code in (0, 1), err
    return report, cites


class TestSegmentation:
    def test_concat_invariant_and_overlap(self, br):
        raw = "abcdefghij"
        segments = br.segment_document(raw, [(2, 6, "x"), (4, 8, "y")])
        assert "".join(s["text"] for s in segments) == raw
        # The overlapping region carries both marks.
        overlap = [s for s in segments if s["marks"] == ["x", "y"]]
        assert overlap and overlap[0]["text"] == "ef"

    def test_empty_and_out_of_range_spans(self, br):
        raw = "abc"
        segments = br.segment_document(raw, [(1, 1, "empty"), (-5, 99, "wide")])
        assert "".join(s["text"] for s in segments) == raw
        assert all("empty" not in s["marks"] for s in segments)
        assert all("wide" in s["marks"] for s in segments)

    def test_binds_hash(self, br):
        expected = hashlib.sha256("A\x00B".encode("utf-8")).hexdigest()
        assert br.binds_hash("A", "B") == expected


class TestBuildCLI:
    def test_happy_path_round_trip(self, tmp_path, H):
        _, cites = _verified_project(tmp_path, H)
        code, out, err = H.run_build(tmp_path)
        assert code == 0, err
        html = (tmp_path / "review.html").read_text(encoding="utf-8")
        payload = H.extract_payload(html)
        assert payload["mode"] == "standalone"
        # Round-trip integrity: segment concatenation equals the file on disk.
        memo_raw = (tmp_path / "memo.md").read_bytes().decode("utf-8")
        assert "".join(s["text"] for s in payload["memo_doc"]["segments"]) == memo_raw
        for key, doc in payload["source_docs"].items():
            src_raw = (tmp_path / cites["sources"][key]["path"]).read_bytes().decode("utf-8")
            assert "".join(s["text"] for s in doc["segments"]) == src_raw
        # Binds present for every citation.
        assert set(payload["binds"]) == {c["id"] for c in cites["citations"]}

    def test_checksum_mismatch_refuses(self, tmp_path, H):
        _verified_project(tmp_path, H)
        target = tmp_path / "sources" / "smith_v_jones_12345.md"
        target.write_text(target.read_text(encoding="utf-8") + "\ntampered",
                          encoding="utf-8")
        code, out, err = H.run_build(tmp_path)
        assert code == 2
        assert "smith_v_jones_12345.md" in err
        assert not (tmp_path / "review.html").exists()

    def test_force_suppresses_highlights_and_flags(self, tmp_path, H):
        _verified_project(tmp_path, H)
        target = tmp_path / "sources" / "smith_v_jones_12345.md"
        target.write_text(target.read_text(encoding="utf-8") + "\ntampered",
                          encoding="utf-8")
        code, out, err = H.run_build(tmp_path, ["--force"])
        assert code == 0
        payload = H.extract_payload((tmp_path / "review.html").read_text(encoding="utf-8"))
        assert payload["build"]["forced"] is True
        assert "sources/smith_v_jones_12345.md" in payload["build"]["mismatches"]
        doc = payload["source_docs"]["cl-12345"]
        assert doc["checksum_ok"] is False
        assert len(doc["segments"]) == 1 and doc["segments"][0]["marks"] == []
        # Untouched statute keeps its highlights.
        assert payload["source_docs"]["stat-tex_prop_code_92_006"]["checksum_ok"] is True

    def test_adversarial_source_cannot_break_out(self, tmp_path, H):
        evil = "</script><script>alert(1)</script> <!-- --> & ampersand"
        _, cites = _verified_project(
            tmp_path, H, citing_snippet=evil)
        template = (H.SKILL_DIR / "viewer" / "review_viewer.html").read_text(encoding="utf-8")
        code, out, err = H.run_build(tmp_path)
        assert code == 0, err
        html = (tmp_path / "review.html").read_text(encoding="utf-8")
        # No new closing script tags beyond the template's own.
        assert html.count("</script") == template.count("</script")
        # And the document text survives the round trip byte-identically.
        payload = H.extract_payload(html)
        src_raw = (tmp_path / "sources" / "smith_v_jones_12345.md").read_bytes().decode("utf-8")
        assert "".join(s["text"] for s in payload["source_docs"]["cl-12345"]["segments"]) == src_raw
        assert evil in src_raw

    def test_prior_review_embedding(self, tmp_path, H, br):
        _, cites = _verified_project(tmp_path, H)
        c0 = cites["citations"][0]
        review = {
            "schema_version": 1,
            "reviews": {
                c0["id"]: {
                    "verdict": "verified", "note": "", "reviewer": "kd",
                    "at": "2026-06-12T00:00:00Z",
                    "binds_to": br.binds_hash(c0["cite_text"], c0["proposition"]),
                }
            },
        }
        (tmp_path / "review.json").write_text(json.dumps(review), encoding="utf-8")
        code, out, err = H.run_build(tmp_path, ["--review", "review.json"])
        assert code == 0, err
        payload = H.extract_payload((tmp_path / "review.html").read_text(encoding="utf-8"))
        assert payload["prior_review"]["reviews"][c0["id"]]["verdict"] == "verified"

    def test_missing_source_renders_missing_doc(self, tmp_path, H):
        H.write_project(tmp_path)
        sources = H.base_proposals([])["sources"]
        sources["cl-404"] = {"type": "opinion", "missing": True, "case_name": "Gone v. Away"}
        citations = [
            H.citation("c001", quotes=[
                'The "totality of the circumstances" governs our review.']),
            H.citation("c002", source="cl-404", cite_text="Id. at 462.",
                       memo_context="starts only at discovery of the injury. Id. at 462.",
                       proposition="Unverifiable proposition.", quotes=["anything"]),
        ]
        code, _, cites, err = H.run_cli(tmp_path, H.base_proposals(citations, sources=sources))
        assert code == 0, err
        code, out, err = H.run_build(tmp_path)
        assert code == 0, err
        payload = H.extract_payload((tmp_path / "review.html").read_text(encoding="utf-8"))
        assert payload["source_docs"]["cl-404"]["missing"] is True

    def test_brand_mark_is_inline_svg_not_data_image(self, tmp_path, H):
        # The bundled viewer's dog must be CSP-safe inline SVG, not a data:
        # <img> (blocked by the MCP App iframe CSP).
        _verified_project(tmp_path, H)
        code, out, err = H.run_build(tmp_path)
        assert code == 0, err
        html = (tmp_path / "review.html").read_text(encoding="utf-8")
        assert "data:image" not in html
        assert "var DOG_SVG" in html and "<rect" in html

    def test_no_external_references(self, tmp_path, H):
        _verified_project(tmp_path, H)
        H.run_build(tmp_path)
        html = (tmp_path / "review.html").read_text(encoding="utf-8")
        for marker in ('src="http', "src='http", 'href="http', "href='http",
                       "@import", "url(http"):
            assert marker not in html

    def test_bad_template_exit_two(self, tmp_path, H):
        _verified_project(tmp_path, H)
        bogus = tmp_path / "tpl.html"
        bogus.write_text("<html>no placeholder</html>", encoding="utf-8")
        code, out, err = H.run_build(tmp_path, ["--template", str(bogus)])
        assert code == 2 and "placeholder" in err

    def test_malformed_cites_exit_two(self, tmp_path, H):
        H.write_project(tmp_path)
        (tmp_path / "cites.json").write_text('{"schema_version": 2}', encoding="utf-8")
        code, out, err = H.run_build(tmp_path)
        assert code == 2 and "schema_version" in err

    def test_non_utf8_source_exits_two_cleanly(self, tmp_path, H):
        # A file that turns non-UTF-8 after verification must exit 2 with a
        # clean message, not crash with a traceback.
        _verified_project(tmp_path, H)
        (tmp_path / "sources" / "smith_v_jones_12345.md").write_bytes(b"\xff\xfe not utf8")
        code, out, err = H.run_build(tmp_path, ["--force"])
        assert code == 2
        assert "UTF-8" in err and "Traceback" not in err
        assert not (tmp_path / "review.html").exists()

    def test_anchor_pages_computed_from_markers(self, tmp_path, H):
        # A page-marked document source: each anchor must map to the page
        # whose <<pg. N>> marker most recently precedes it.
        doc_text = ("<<pg. 461>>\nIntro text on page four sixty one.\n"
                    "<<pg. 462>>\nThe corporation waived its objection on the record.\n"
                    "<<pg. 463>>\nClosing remarks.\n")
        memo = (H.DEFAULT_MEMO +
                "The objection was waived on the record. Smith Dep. 462:2.\n")
        H.write_project(tmp_path, memo=memo, sources={
            "sources/smith_v_jones_12345.md": H.make_opinion_md(),
            "sources/depo_smith.md": doc_text,
        })
        sources = {
            "cl-12345": {
                "type": "opinion", "path": "sources/smith_v_jones_12345.md",
                "cluster_id": "12345", "case_name": "Smith v. Jones",
                "citation": "123 F.3d 456",
            },
            "doc-depo_smith": {
                "type": "document", "path": "sources/depo_smith.md",
                "title": "Smith Deposition", "kind": "evidence",
                "render_hint": "transcript",
            },
        }
        citations = [
            H.citation("c001", source="doc-depo_smith",
                       cite_text="Smith Dep. 462:2.",
                       proposition="The objection was waived.",
                       quotes=["The corporation waived its objection"]),
        ]
        code, _, cites, err = H.run_cli(tmp_path, H.base_proposals(citations, sources=sources))
        assert code == 0, err
        code, out, err = H.run_build(tmp_path)
        assert code == 0, err
        payload = H.extract_payload((tmp_path / "review.html").read_text(encoding="utf-8"))
        assert payload["source_docs"]["doc-depo_smith"]["anchor_pages"] == {"c001:0": 462}
        # Unmarked sources carry no anchor_pages key at all.
        assert "anchor_pages" not in payload["source_docs"]["cl-12345"]
        # render_hint rides through cites for the viewer's transcript mode.
        assert payload["cites"]["sources"]["doc-depo_smith"]["render_hint"] == "transcript"


def _project_with_original(tmp_path, H, original_bytes=b"%PDF-1.7 fake",
                           media_type="application/pdf"):
    """Verified project where the opinion source carries an original binary."""
    H.write_project(tmp_path)
    orig = tmp_path / "sources" / "originals" / "smith.pdf"
    orig.parent.mkdir(parents=True)
    orig.write_bytes(original_bytes)
    proposals = H.base_proposals([
        H.citation("c001", quotes=[
            'The "totality of the circumstances" governs our review.']),
    ])
    proposals["sources"]["cl-12345"]["original"] = {
        "path": "sources/originals/smith.pdf",
        "media_type": media_type,
        "pages": 3,
    }
    code, _, cites, err = H.run_cli(tmp_path, proposals)
    assert code == 0, err
    return orig, cites


class TestOriginalsEmbedding:
    def test_pdf_embeds_with_vendor_libs(self, tmp_path, H):
        import base64
        orig, cites = _project_with_original(tmp_path, H)
        code, out, err = H.run_build(tmp_path)
        assert code == 0, err
        html = (tmp_path / "review.html").read_text(encoding="utf-8")
        payload = H.extract_payload(html)
        entry = payload["originals"]["cl-12345"]
        # Byte-exact round trip of the original file.
        assert base64.b64decode(entry["data_b64"]) == orig.read_bytes()
        assert entry["media_type"] == "application/pdf"
        assert entry["pages"] == 3
        assert payload["originals_skipped"] == []
        # Only the PDF vendor libs ride along; DOCX libs stay out.
        assert 'id="cc-vendor-pdfjs"' in html
        assert 'id="cc-vendor-pdfjs-worker"' in html
        assert 'id="cc-vendor-docx-preview"' not in html
        assert 'id="cc-vendor-jszip"' not in html
        # Vendor code rides as inert base64, never as executable script src.
        assert 'type="text/plain" id="cc-vendor-pdfjs"' in html

    def test_no_originals_flag_skips_everything(self, tmp_path, H):
        _project_with_original(tmp_path, H)
        code, out, err = H.run_build(tmp_path, ["--no-originals"])
        assert code == 0, err
        html = (tmp_path / "review.html").read_text(encoding="utf-8")
        payload = H.extract_payload(html)
        assert payload["originals"] == {}
        assert payload["originals_skipped"] == [
            {"key": "cl-12345", "reason": "disabled"}]
        # No inert vendor payload tags (the viewer JS naming the ids is fine).
        assert 'type="text/plain" id="cc-vendor-' not in html

    def test_missing_original_skips_not_fatal(self, tmp_path, H):
        orig, _ = _project_with_original(tmp_path, H)
        orig.unlink()
        code, out, err = H.run_build(tmp_path)
        assert code == 0, err
        payload = H.extract_payload((tmp_path / "review.html").read_text(encoding="utf-8"))
        assert payload["originals"] == {}
        assert payload["originals_skipped"] == [
            {"key": "cl-12345", "reason": "missing"}]
        assert "text only" in err

    def test_changed_original_fatal_then_force_skips(self, tmp_path, H):
        orig, _ = _project_with_original(tmp_path, H)
        orig.write_bytes(b"%PDF-1.7 tampered")
        code, out, err = H.run_build(tmp_path)
        assert code == 2
        assert "original document changed" in err
        code, out, err = H.run_build(tmp_path, ["--force"])
        assert code == 0, err
        payload = H.extract_payload((tmp_path / "review.html").read_text(encoding="utf-8"))
        assert payload["originals"] == {}
        assert payload["originals_skipped"] == [
            {"key": "cl-12345", "reason": "checksum_mismatch"}]
        # The verified TEXT view is unaffected by a stale original.
        assert payload["source_docs"]["cl-12345"]["checksum_ok"] is True
        assert payload["build"]["forced"] is False

    def test_oversized_original_skipped(self, tmp_path, H, br, monkeypatch):
        orig, cites = _project_with_original(tmp_path, H)
        monkeypatch.setattr(br, "MAX_ORIGINAL_BYTES", 4)
        originals, skipped, failures = br.embed_originals(cites, tmp_path)
        assert originals == {}
        assert skipped == [{"key": "cl-12345", "reason": "too_large"}]
        assert failures == []

    def test_text_plain_original_not_embedded(self, tmp_path, H, br):
        # text/plain originals are provenance metadata; the viewer has no
        # native text-file renderer, so embedding the bytes is dead weight.
        orig, cites = _project_with_original(tmp_path, H,
                                             media_type="text/plain")
        originals, skipped, failures = br.embed_originals(cites, tmp_path)
        assert originals == {}
        assert skipped == [{"key": "cl-12345", "reason": "not_renderable"}]
        assert failures == []

    def test_first_page_emitted_for_offset_exhibits(self, tmp_path, H):
        # --first-page exhibits: printed numbers start at 461, so the viewer
        # needs first_page to map printed pages back to PDF ordinals.
        doc_text = ("<<pg. 461>>\nIntro.\n"
                    "<<pg. 462>>\nThe corporation waived its objection.\n")
        memo = H.DEFAULT_MEMO + "Waiver on the record. Ex. A at 462.\n"
        H.write_project(tmp_path, memo=memo, sources={
            "sources/smith_v_jones_12345.md": H.make_opinion_md(),
            "sources/tex_prop_code_92_006.md": H.make_statute_md(),
            "sources/exhibit_a.md": doc_text,
        })
        sources = H.base_proposals([])["sources"]
        sources["doc-exhibit_a"] = {"type": "document",
                                    "path": "sources/exhibit_a.md",
                                    "title": "Exhibit A", "kind": "evidence"}
        citations = [H.citation("c001", source="doc-exhibit_a",
                                cite_text="Ex. A at 462.",
                                proposition="The objection was waived.",
                                quotes=["The corporation waived its objection"])]
        code, _, cites, err = H.run_cli(tmp_path, H.base_proposals(citations, sources=sources))
        assert code == 0, err
        code, out, err = H.run_build(tmp_path)
        assert code == 0, err
        payload = H.extract_payload((tmp_path / "review.html").read_text(encoding="utf-8"))
        doc = payload["source_docs"]["doc-exhibit_a"]
        assert doc["anchor_pages"] == {"c001:0": 462}
        assert doc["first_page"] == 461

    def test_vendor_manifest_drift_is_fatal(self, tmp_path, H, br):
        # A tampered vendored library must never be embedded silently.
        vendor = tmp_path / "vendor"
        (vendor / "pdfjs").mkdir(parents=True)
        (vendor / "pdfjs" / "pdf.min.mjs").write_text("tampered", encoding="utf-8")
        (vendor / "pdfjs" / "pdf.worker.min.mjs").write_text("w", encoding="utf-8")
        (vendor / "MANIFEST.json").write_text(json.dumps({"libraries": [
            {"name": "pdfjs-dist (main)", "file": "pdfjs/pdf.min.mjs",
             "version": "0", "sha256": "0" * 64, "license": "Apache-2.0"},
            {"name": "pdfjs-dist (worker)", "file": "pdfjs/pdf.worker.min.mjs",
             "version": "0", "sha256": "1" * 64, "license": "Apache-2.0"},
        ]}), encoding="utf-8")
        payload = {"originals": {"cl-1": {"media_type": "application/pdf",
                                          "data_b64": "", "sha256": None}}}
        with pytest.raises(br.FatalError, match="does not match MANIFEST"):
            br.render_vendor_block(payload, vendor)

    def test_real_vendor_dir_passes_manifest_check(self, tmp_path, H, br):
        # The shipped vendor tree must satisfy its own manifest.
        payload = {"originals": {
            "a": {"media_type": "application/pdf", "data_b64": ""},
            "b": {"media_type": "application/vnd.openxmlformats-officedocument"
                               ".wordprocessingml.document", "data_b64": ""},
        }}
        block = br.render_vendor_block(payload, H.SKILL_DIR / "viewer" / "vendor")
        for tag_id in ("cc-vendor-pdfjs", "cc-vendor-pdfjs-worker",
                       "cc-vendor-docx-preview", "cc-vendor-jszip"):
            assert tag_id in block
        assert "Apache-2.0" in block   # license notice comment
