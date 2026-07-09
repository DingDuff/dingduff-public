"""Phase-2 tests: cite-checking against attorney-supplied 'document' sources
(a Restatement section, an off-CourtListener case, an opposing brief, a PDF
extracted to text) — not just DingDuff-hosted opinions/statutes."""

import json

import pytest


RESTATEMENT = (
    "# Restatement (Second) of Torts § 46\n\n"
    "One who by extreme and outrageous conduct intentionally or recklessly "
    "causes severe emotional distress to another is subject to liability for "
    "such emotional distress, and if bodily harm to the other results from it, "
    "for such bodily harm.\n"
)

# A working file may itself contain a "## Citing Cases" heading; for documents
# there is no body guard, so text after it must remain quotable.
OFF_CL_CASE = (
    "# Acme Corp. v. Beta LLC (unreported)\n\n"
    "The court held that a forum-selection clause is presumptively valid and "
    "will be enforced absent a strong showing that enforcement is unreasonable.\n\n"
    "## Citing Cases\n\n"
    "Later courts have narrowed this holding considerably.\n"
)

MEMO = (
    "# Memo\n\n"
    "Liability attaches for extreme and outrageous conduct. "
    "Restatement (Second) of Torts § 46. The forum clause is enforceable. "
    "Acme Corp. v. Beta LLC (unreported).\n"
)


def _doc_sources():
    return {
        "doc-restatement_torts_46": {
            "type": "document",
            "path": "sources/restatement_torts_46.md",
            "title": "Restatement (Second) of Torts § 46",
            "kind": "secondary",
        },
        "doc-acme_v_beta": {
            "type": "document",
            "path": "sources/acme_v_beta.md",
            "title": "Acme Corp. v. Beta LLC (unreported)",
            "kind": "case",
        },
    }


def _write(tmp_path):
    (tmp_path / "memo.md").write_text(MEMO, encoding="utf-8")
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "restatement_torts_46.md").write_text(RESTATEMENT, encoding="utf-8")
    (tmp_path / "sources" / "acme_v_beta.md").write_text(OFF_CL_CASE, encoding="utf-8")


class TestDocumentVerifier:
    def test_document_source_anchors(self, tmp_path, H):
        _write(tmp_path)
        proposals = H.base_proposals([
            H.citation(
                cid="c001", source="doc-restatement_torts_46",
                cite_text="Restatement (Second) of Torts § 46",
                proposition="Extreme and outrageous conduct causing severe distress is actionable.",
                quotes=["extreme and outrageous conduct intentionally or recklessly "
                        "causes severe emotional distress"]),
            H.citation(
                cid="c002", source="doc-acme_v_beta",
                cite_text="Acme Corp. v. Beta LLC (unreported)",
                proposition="Forum-selection clauses are presumptively valid.",
                quotes=["a forum-selection clause is presumptively valid"]),
        ], sources=_doc_sources())
        code, report, cites, stderr = H.run_cli(tmp_path, proposals)
        assert code == 0, stderr
        assert [c["status"] for c in cites["citations"]] == ["anchored", "anchored"]
        # title/kind pass through to cites.json
        s = cites["sources"]["doc-restatement_torts_46"]
        assert s["title"].startswith("Restatement") and s["kind"] == "secondary"
        H.assert_anchor_invariant(tmp_path, cites)

    def test_no_body_guard_for_documents(self, tmp_path, H):
        """Text after a '## Citing Cases' line in a document is still quotable."""
        _write(tmp_path)
        proposals = H.base_proposals([
            H.citation(
                cid="c001", source="doc-acme_v_beta",
                cite_text="Acme Corp. v. Beta LLC (unreported)",
                proposition="Later courts narrowed the holding.",
                quotes=["Later courts have narrowed this holding considerably"]),
        ], sources={"doc-acme_v_beta": _doc_sources()["doc-acme_v_beta"]})
        code, report, cites, stderr = H.run_cli(tmp_path, proposals)
        assert code == 0, stderr
        assert cites["citations"][0]["status"] == "anchored"

    def test_hallucinated_quote_fails(self, tmp_path, H):
        _write(tmp_path)
        proposals = H.base_proposals([
            H.citation(
                cid="c001", source="doc-restatement_torts_46",
                cite_text="Restatement (Second) of Torts § 46",
                proposition="Made-up proposition.",
                quotes=["punitive damages are always recoverable for negligence"]),
        ], sources={"doc-restatement_torts_46": _doc_sources()["doc-restatement_torts_46"]})
        code, report, cites, stderr = H.run_cli(tmp_path, proposals)
        assert code == 1
        assert cites["citations"][0]["status"] == "anchor_failed"
        assert cites["citations"][0]["failure_reason"] == "not_found"

    def test_mixed_hosted_and_document_sources(self, tmp_path, H):
        """A hosted opinion and a working document in the same run."""
        _write(tmp_path)
        (tmp_path / "sources" / "smith_v_jones_12345.md").write_text(
            H.make_opinion_md(), encoding="utf-8")
        memo = MEMO.rstrip("\n") + (
            " The discovery rule controls. Smith v. Jones, 123 F.3d 456, 461 "
            "(9th Cir. 1997).\n")
        (tmp_path / "memo.md").write_text(memo, encoding="utf-8")
        sources = dict(_doc_sources())
        sources["cl-12345"] = {
            "type": "opinion", "path": "sources/smith_v_jones_12345.md",
            "cluster_id": "12345", "case_name": "Smith v. Jones",
            "citation": "123 F.3d 456",
        }
        proposals = H.base_proposals([
            H.citation(cid="c001", source="doc-restatement_torts_46",
                       cite_text="Restatement (Second) of Torts § 46",
                       proposition="Outrageous conduct is actionable.",
                       quotes=["extreme and outrageous conduct"]),
            H.citation(cid="c002", source="cl-12345",
                       cite_text="Smith v. Jones, 123 F.3d 456, 461 (9th Cir. 1997)",
                       proposition="The discovery rule governs accrual.",
                       quotes=["The limitations period does not begin to run until"]),
        ], sources=sources)
        code, report, cites, stderr = H.run_cli(tmp_path, proposals)
        assert code == 0, stderr
        assert {c["status"] for c in cites["citations"]} == {"anchored"}
        H.assert_anchor_invariant(tmp_path, cites)


class TestDocumentStandaloneBundle:
    """The standalone review.html embeds document sources from disk (no server)."""

    def test_build_review_embeds_and_highlights_document(self, tmp_path, H):
        _write(tmp_path)
        proposals = H.base_proposals([
            H.citation(
                cid="c001", source="doc-restatement_torts_46",
                cite_text="Restatement (Second) of Torts § 46",
                proposition="Outrageous conduct causing severe distress is actionable.",
                support_type="quotation",
                quotes=["extreme and outrageous conduct intentionally or recklessly "
                        "causes severe emotional distress"]),
        ], sources={"doc-restatement_torts_46": _doc_sources()["doc-restatement_torts_46"]})
        code, report, cites, stderr = H.run_cli(tmp_path, proposals)
        assert code == 0, stderr

        bcode, out, err = H.run_build(tmp_path)
        assert bcode == 0, err
        payload = H.extract_payload((tmp_path / "review.html").read_text(encoding="utf-8"))
        doc = payload["source_docs"]["doc-restatement_torts_46"]
        # Embedded verbatim (segments concatenate back to the file on disk)…
        raw = (tmp_path / "sources" / "restatement_torts_46.md").read_bytes().decode("utf-8")
        assert "".join(s["text"] for s in doc["segments"]) == raw
        # …and the anchored quote produced a highlight segment for c001.
        assert any(any(m.startswith("c001:") for m in s["marks"]) for s in doc["segments"])
