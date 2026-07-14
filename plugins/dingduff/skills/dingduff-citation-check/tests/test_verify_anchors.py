"""Tests for verify_anchors.py — the deterministic core of cite-check.

The standing invariant, asserted wherever anchors are produced: every
anchor's quote equals the raw codepoint slice raw[start:end] of its file.
"""

import hashlib
import json

import pytest


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

class TestNormalization:
    def test_vectors(self, va, vectors):
        for v in vectors:
            assert va.normalize_needle(v["input"]) == v["expected"], v["name"]

    def test_span_map_round_trip(self, va):
        raw = "He said “warned…now” — twice"
        norm, starts, ends = va.normalize_with_map(raw)
        assert len(starts) == len(ends) == len(norm)
        # Every span is well-formed and monotonically non-decreasing.
        assert all(0 <= s < e <= len(raw) for s, e in zip(starts, ends))
        assert all(a <= b for a, b in zip(starts, starts[1:]))
        # The ellipsis expansion maps all three dots to the single raw char.
        dot = norm.index("...")
        assert starts[dot] == starts[dot + 1] == starts[dot + 2] == raw.index("…")

    def test_map_slices_back_to_raw(self, va):
        raw = "the “totality   of\nthe circumstances” test"
        norm, starts, ends = va.normalize_with_map(raw)
        needle = 'the "totality of the circumstances" test'
        pos = norm.find(needle)
        assert pos != -1
        start, end = starts[pos], ends[pos + len(needle) - 1]
        assert raw[start:end] == raw  # spans the whole string here

    def test_entity_span_covers_whole_reference(self, va):
        # A normalized char produced by an entity must map to the FULL raw
        # entity span — a quote ending on it must not cut '&amp;' in half.
        raw = "argued by McGuire &amp; Levy"
        norm, starts, ends = va.normalize_with_map(raw)
        amp = norm.index("&")
        assert raw[starts[amp]:ends[amp]] == "&amp;"


# ---------------------------------------------------------------------------
# Source anchoring
# ---------------------------------------------------------------------------

@pytest.fixture()
def opinion_doc(va, H):
    return va.Document(H.make_opinion_md())


def _single_anchor(va, doc, quote, max_gap=2000):
    anchors, failure, warnings = va.anchor_quote(doc, quote, max_gap)
    return anchors, failure, warnings


class TestSourceAnchoring:
    def test_exact_tier(self, va, opinion_doc):
        quote = "The limitations period does not begin to run until the plaintiff knows"
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure is None
        assert anchors[0].match == "exact"
        assert opinion_doc.raw[anchors[0].start:anchors[0].end] == quote

    def test_normalized_curly_quotes(self, va, opinion_doc):
        quote = 'The "totality of the circumstances" governs our review.'
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure is None
        assert anchors[0].match == "normalized"
        # The stored quote is the RAW slice (curly quotes preserved).
        sliced = opinion_doc.raw[anchors[0].start:anchors[0].end]
        assert sliced == anchors[0].quote
        assert "“" in sliced and "”" in sliced

    def test_normalized_em_dash(self, va, opinion_doc):
        quote = "This principle-deeply rooted in our precedent-admits of no exception."
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure is None
        assert "—" in anchors[0].quote

    def test_dehyphenation_across_linebreak(self, va, opinion_doc):
        quote = "a reasonable expectation of privacy in the place searched"
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure is None
        assert "expecta-\ntion" in anchors[0].quote

    def test_tier2_genuine_compound(self, va, opinion_doc):
        # Source has "well-\nknown" (de-hyphenated by rule 6 into "wellknown");
        # the quote's genuine compound "well-known" only matches via tier 2.
        quote = "A well-known corollary follows from that rule."
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure is None
        assert anchors[0].match == "normalized"
        assert "well-\nknown" in anchors[0].quote

    def test_whitespace_collapse(self, va, H):
        doc = va.Document(H.make_opinion_md(
            body="The rule   requires\n\tthe court to act."))
        anchors, failure, _ = _single_anchor(va, doc, "The rule requires the court to act.")
        assert failure is None

    def test_case_mismatch_hint(self, va, opinion_doc):
        quote = "the limitations period does not begin to run until the plaintiff knows"
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert anchors is None
        assert failure.reason == "case_mismatch"
        assert failure.hint.startswith("The limitations period")

    def test_not_found_prefix_hint(self, va, opinion_doc):
        quote = ("The limitations period does not begin to run until the moon "
                 "is in the seventh house")
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure.reason == "not_found"
        assert "limitations period" in failure.hint

    def test_multiple_matches_warning(self, va, H):
        body = "The rule applies with full force. Filler. The rule applies with full force."
        doc = va.Document(H.make_opinion_md(body=body))
        anchors, failure, warnings = _single_anchor(va, doc, "The rule applies with full force.")
        assert failure is None
        assert any(w["code"] == "multiple_matches" for w in warnings)
        assert anchors[0].start == doc.raw.index("The rule applies")

    def test_short_quote_warning(self, va, opinion_doc):
        anchors, failure, warnings = _single_anchor(va, opinion_doc, "no exception")
        assert failure is None
        assert any(w["code"] == "short_quote" for w in warnings)

    def test_match_in_header_warning(self, va, H):
        doc = va.Document(H.make_opinion_md())
        anchors, failure, warnings = _single_anchor(
            va, doc, "**Date Filed:** 1997-03-15")
        assert failure is None
        assert any(w["code"] == "match_in_header" for w in warnings)

    def test_only_in_citing_cases(self, va, H):
        doc = va.Document(H.make_opinion_md(
            citing_snippet="equitable tolling saves an otherwise untimely claim"))
        anchors, failure, _ = _single_anchor(
            va, doc, "equitable tolling saves an otherwise untimely claim")
        assert anchors is None
        assert failure.reason == "only_in_citing_cases"

    def test_body_beats_citing_cases(self, va, H):
        phrase = "the discovery rule postpones accrual of the claim"
        doc = va.Document(H.make_opinion_md(
            body=f"We hold that {phrase}. Nothing more is required.",
            citing_snippet=phrase))
        anchors, failure, _ = _single_anchor(va, doc, phrase)
        assert failure is None
        assert anchors[0].start < doc.body_end

    def test_entity_bearing_source_matches_clean_quote(self, va, H):
        # Live repro (859 S.W.2d 107): CourtListener text carries literal
        # HTML entities into stored files. A clean quote must still anchor,
        # and the raw slice keeps the entities intact (slice invariant).
        body = ("brought under the Deceptive Trade Practices Act, TEX.BUS. "
                "&amp; COM.CODE ANN. &sect;&#160;17.41, when the landlord"
                "&#x27;s agent failed to act.&#13;\nNothing more is required "
                "of the tenant in this posture.")
        doc = va.Document(H.make_opinion_md(body=body))
        quote = ("TEX.BUS. & COM.CODE ANN. § 17.41, when the landlord's "
                 "agent failed to act.")
        anchors, failure, _ = _single_anchor(va, doc, quote)
        assert failure is None
        assert anchors[0].match == "normalized"
        sliced = doc.raw[anchors[0].start:anchors[0].end]
        assert sliced == anchors[0].quote
        assert "&amp;" in sliced and "&#x27;" in sliced

    def test_normalized_match_ending_on_entity_keeps_it_whole(self, va, H):
        # The quote's newline forces the normalized tier (tier-0 exact would
        # otherwise legitimately match the literal '&' inside '&amp;'). A
        # normalized match ending on a decoded entity must map its end to the
        # FULL raw reference, not one char past its first byte.
        body = "fees were sought by the firm of McGuire &amp; Levy of Dallas."
        doc = va.Document(H.make_opinion_md(body=body))
        anchors, failure, _ = _single_anchor(
            va, doc, "fees were sought by the firm\nof McGuire &")
        assert failure is None
        assert anchors[0].match == "normalized"
        assert doc.raw[anchors[0].start:anchors[0].end].endswith("&amp;")

    def test_entity_quote_matches_clean_source(self, va, H):
        # Reverse direction: the stored file is clean but the proposed quote
        # carries entities (e.g. copied from an older entity-bearing copy).
        body = "The DTPA, TEX.BUS. & COM.CODE ANN. § 17.41, governs this claim."
        doc = va.Document(H.make_opinion_md(body=body))
        anchors, failure, _ = _single_anchor(
            va, doc, "TEX.BUS. &amp; COM.CODE ANN. &sect;&#160;17.41, governs this claim.")
        assert failure is None

    def test_statute_no_citing_section(self, va, H):
        doc = va.Document(H.make_statute_md())
        assert doc.body_end == len(doc.raw)
        quote = "The landlord shall test each smoke alarm at the beginning of the tenant's possession."
        anchors, failure, _ = _single_anchor(va, doc, quote)
        assert failure is None
        assert doc.raw[anchors[0].start:anchors[0].end] == anchors[0].quote


class TestRendererMarkdownAnchoring:
    """opinion_store's html_to_markdown renderer emits `> ` block quotes,
    `[^n]` footnote marks and `<<pg. N>>` page markers; all three are
    zero-width during matching so quotes spanning them still anchor."""

    def test_quote_spanning_blockquote_paragraphs(self, va, H):
        body = (
            "The manual instructs:\n\n"
            "> The guilt of the subject is to be posited as a fact.\n\n"
            "> Interrogation should proceed without pause."
        )
        doc = va.Document(H.make_opinion_md(body=body))
        quote = ("The guilt of the subject is to be posited as a fact. "
                 "Interrogation should proceed without pause.")
        anchors, failure, _ = _single_anchor(va, doc, quote)
        assert failure is None
        assert anchors[0].match == "normalized"
        # The raw slice keeps the renderer's `> ` prefix.
        assert "\n> Interrogation" in anchors[0].quote

    def test_quote_spanning_footnote_mark(self, va, H):
        body = ("Both courts arrived at varying conclusions.[^1] A wealth of "
                "scholarly material followed.")
        doc = va.Document(H.make_opinion_md(body=body))
        quote = "arrived at varying conclusions. A wealth of scholarly material"
        anchors, failure, _ = _single_anchor(va, doc, quote)
        assert failure is None
        assert "[^1]" in anchors[0].quote

    def test_footnote_definition_body_quotable(self, va, H):
        body = ("The rule was applied.[^2]\n\n**Footnotes**\n\n"
                "[^2]: Compare the earlier decisions rejecting this approach.")
        doc = va.Document(H.make_opinion_md(body=body))
        anchors, failure, _ = _single_anchor(
            va, doc, "Compare the earlier decisions rejecting this approach.")
        assert failure is None

    def test_bracketed_number_still_content(self, va, H):
        # NY-style bracket cites must NOT be skipped: `[^n]` only.
        body = "The motion was made under CPLR 3211[a][7] and denied."
        doc = va.Document(H.make_opinion_md(body=body))
        anchors, failure, _ = _single_anchor(
            va, doc, "under CPLR 3211[a][7] and denied")
        assert failure is None
        assert anchors[0].match == "exact"


class TestEllipsisAnchoring:
    def test_two_segments(self, va, opinion_doc):
        quote = ("The limitations period does not begin to run ... that forms "
                 "the basis of the action.")
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure is None
        assert len(anchors) == 2
        assert anchors[0].end <= anchors[1].start
        for a in anchors:
            assert opinion_doc.raw[a.start:a.end] == a.quote

    def test_ellipsis_char_equivalent(self, va, opinion_doc):
        quote = ("The limitations period does not begin to run … that forms "
                 "the basis of the action.")
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure is None and len(anchors) == 2

    def test_out_of_order_segments(self, va, opinion_doc):
        quote = ("that forms the basis of the action. ... The limitations "
                 "period does not begin to run")
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert anchors is None
        assert failure.reason == "not_found"
        assert "document order" in failure.hint

    def test_gap_too_large(self, va, opinion_doc):
        quote = ("The limitations period does not begin to run ... absent "
                 "proof of actual harm to the claimant.")
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote, max_gap=10)
        assert failure.reason == "ellipsis_gap_too_large"

    def test_segment_too_short(self, va, opinion_doc):
        quote = "The limitations period does not begin to run ... action"
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure.reason == "segment_too_short"

    def test_edge_ellipses_are_trimming(self, va, opinion_doc):
        quote = "... knows or has reason to know of the injury ..."
        anchors, failure, _ = _single_anchor(va, opinion_doc, quote)
        assert failure is None
        assert len(anchors) == 1


# ---------------------------------------------------------------------------
# Memo anchoring
# ---------------------------------------------------------------------------

class TestMemoAnchoring:
    @pytest.fixture()
    def memo_doc(self, va, H):
        doc = va.Document(H.DEFAULT_MEMO)
        return doc

    def test_unique_cite(self, va, memo_doc):
        span, failure = va.anchor_memo(
            memo_doc, "Smith v. Jones, 123 F.3d 456, 461 (9th Cir. 1997)", None)
        assert failure is None
        assert memo_doc.raw[span[0]:span[1]].startswith("Smith v. Jones")

    def test_id_chain_disambiguated(self, va, memo_doc):
        span1, f1 = va.anchor_memo(
            memo_doc, "Id. at 462.", "starts only at discovery of the injury. Id. at 462.")
        span2, f2 = va.anchor_memo(
            memo_doc, "Id. at 463.", "privacy in the place searched. Id. at 463.")
        assert f1 is None and f2 is None
        assert span1 != span2
        assert memo_doc.raw[span1[0]:span1[1]] == "Id. at 462."
        assert memo_doc.raw[span2[0]:span2[1]] == "Id. at 463."

    def test_ambiguous_without_context(self, va, H):
        memo = "See Id. at 4. More text. See Id. at 4. The end."
        doc = va.Document(memo)
        span, failure = va.anchor_memo(doc, "Id. at 4.", None)
        assert failure.reason == "ambiguous_in_memo"

    def test_context_not_found(self, va, memo_doc):
        span, failure = va.anchor_memo(
            memo_doc, "Id. at 462.", "this context is nowhere in the memo")
        # cite is ambiguous in DEFAULT_MEMO? "Id. at 462." occurs once, so
        # context path is not taken — use an ambiguous memo instead.
        memo = "Id. at 9. Filler sentence. Id. at 9."
        doc = va.Document(memo)
        span, failure = va.anchor_memo(doc, "Id. at 9.", "absent context snippet")
        assert failure.reason == "memo_context_not_found"

    def test_cite_not_in_context(self, va):
        memo = "Id. at 9. The court agreed entirely. Id. at 9."
        doc = va.Document(memo)
        span, failure = va.anchor_memo(doc, "Id. at 9.", "court agreed entirely")
        assert failure.reason == "cite_text_not_in_context"

    def test_not_found(self, va, memo_doc):
        span, failure = va.anchor_memo(memo_doc, "Wholly Absent v. Cite, 1 U.S. 1", None)
        assert failure.reason == "not_found"


# ---------------------------------------------------------------------------
# Offset integrity
# ---------------------------------------------------------------------------

class TestOffsetIntegrity:
    def test_astral_chars_before_anchor(self, va, H):
        body = "The symbol 𝒜 denotes the class. The rule requires prompt notice to the insurer."
        doc = va.Document(H.make_opinion_md(body=body))
        quote = "The rule requires prompt notice to the insurer."
        anchors, failure, _ = _single_anchor(va, doc, quote)
        assert failure is None
        assert doc.raw[anchors[0].start:anchors[0].end] == quote

    def test_crlf_file_offsets(self, va, tmp_path, H):
        content = H.make_opinion_md().replace("\n", "\r\n")
        p = tmp_path / "crlf.md"
        p.write_bytes(content.encode("utf-8"))
        raw = va.read_document(p)
        assert "\r\n" in raw  # no newline translation
        doc = va.Document(raw)
        quote = "The limitations period does not begin to run until the plaintiff knows"
        anchors, failure, _ = _single_anchor(va, doc, quote)
        assert failure is None
        assert raw[anchors[0].start:anchors[0].end] == anchors[0].quote

    def test_sha256_is_over_raw_bytes(self, va, tmp_path):
        p = tmp_path / "f.md"
        p.write_bytes("memo “text”\r\n".encode("utf-8"))
        assert va.sha256_file(p) == hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# CLI contract
# ---------------------------------------------------------------------------

class TestCLI:
    def _good_citations(self, H):
        return [
            H.citation(
                "c001",
                quotes=["The limitations period does not begin to run until the "
                        "plaintiff knows or has reason to know of the injury"],
            ),
            H.citation(
                "c002",
                cite_text="Id. at 463.",
                memo_context="privacy in the place searched. Id. at 463.",
                proposition="A reasonable expectation of privacy is required.",
                quotes=["a reasonable expectation of privacy in the place searched"],
            ),
            H.citation(
                "c003",
                source="stat-tex_prop_code_92_006",
                cite_text="Tex. Prop. Code § 92.006",
                proposition="Landlords must install bedroom smoke alarms.",
                quotes=["A landlord shall install a smoke alarm in each bedroom"],
            ),
        ]

    def test_success_exit_zero(self, tmp_path, H):
        H.write_project(tmp_path)
        code, report, cites, err = H.run_cli(tmp_path, H.base_proposals(self._good_citations(H)))
        assert code == 0, err
        assert report["ok"] is True
        assert report["by_status"] == {"anchored": 3, "anchor_failed": 0, "no_quote_claimed": 0}
        assert cites["schema_version"] == 1
        assert cites["memo"]["sha256"] == hashlib.sha256(
            (tmp_path / "memo.md").read_bytes()).hexdigest()
        assert all(c["status"] == "anchored" for c in cites["citations"])
        assert cites["citations"][0]["anchors"][0]["match"] == "exact"
        c0 = cites["citations"][0]
        assert c0["binds_to"] == hashlib.sha256(
            (c0["cite_text"] + "\x00" + c0["proposition"]).encode()).hexdigest()
        H.assert_anchor_invariant(tmp_path, cites)

    def test_failure_exit_one_then_fix_rerun(self, tmp_path, H):
        H.write_project(tmp_path)
        bad = self._good_citations(H)
        bad[0]["anchors_proposed"] = [{"quote": "this passage simply is not in the opinion"}]
        code, report, cites, _ = H.run_cli(tmp_path, H.base_proposals(bad))
        assert code == 1
        assert report["ok"] is False
        f = report["failed"][0]
        assert {"id", "source", "where", "quote", "reason", "hint"} <= set(f)
        assert f["id"] == "c001" and f["where"] == "source"
        # cites.json still written, with the failure recorded.
        assert cites["citations"][0]["status"] == "anchor_failed"
        assert cites["citations"][0]["failure_reason"] == "not_found"
        # Idempotent retry loop: fix and rerun on the same files.
        code2, report2, cites2, _ = H.run_cli(tmp_path, H.base_proposals(self._good_citations(H)))
        assert code2 == 0 and report2["ok"] is True
        H.assert_anchor_invariant(tmp_path, cites2)

    def test_no_quote_claimed(self, tmp_path, H):
        H.write_project(tmp_path)
        cit = H.citation("c001", no_quote_claimed=True, support_type="paraphrase",
                         proposition="General background.", quotes=[])
        code, report, cites, err = H.run_cli(tmp_path, H.base_proposals([cit]))
        assert code == 0, err
        assert cites["citations"][0]["status"] == "no_quote_claimed"
        assert cites["citations"][0]["anchors"] == []
        assert cites["citations"][0]["memo_anchor"] is not None

    def test_missing_source_passthrough(self, tmp_path, H):
        H.write_project(tmp_path)
        sources = H.base_proposals([])["sources"]
        sources["cl-77777"] = {"type": "opinion", "missing": True,
                               "case_name": "Absent v. Case", "citation": "1 U.S. 1"}
        cit = H.citation("c001", source="cl-77777",
                         cite_text="Smith v. Jones, 123 F.3d 456, 461 (9th Cir. 1997)",
                         quotes=["whatever quote"])
        code, report, cites, err = H.run_cli(
            tmp_path, H.base_proposals([cit], sources=sources))
        # Missing sources are unverifiable, not retryable: exit 0.
        assert code == 0, err
        assert report["unverifiable"] == [
            {"id": "c001", "source": "cl-77777", "reason": "source_missing"}]
        entry = cites["citations"][0]
        assert entry["status"] == "anchor_failed"
        assert entry["failure_reason"] == "source_missing"
        assert cites["sources"]["cl-77777"]["sha256"] is None

    def test_cluster_id_mismatch_warning(self, tmp_path, H):
        H.write_project(tmp_path)
        proposals = H.base_proposals(self._good_citations(H))
        proposals["sources"]["cl-12345"]["cluster_id"] = "99"
        code, report, _, _ = H.run_cli(tmp_path, proposals)
        assert code == 0
        assert any(w["code"] == "cluster_id_mismatch" for w in report["warnings"])

    @pytest.mark.parametrize("mutate, fragment", [
        (lambda p: p["citations"].append(dict(p["citations"][0])), "duplicate citation id"),
        (lambda p: p["citations"][0].update(id="bogus"), "must match c<NNN>"),
        (lambda p: p["citations"][0].update(source="cl-nope"), "unknown source"),
        (lambda p: p["citations"][0].update(anchors_proposed=[]), "at least one quote"),
        (lambda p: p["memo"].pop("path"), "memo.path is required"),
        (lambda p: p.update(schema_version=2), "schema_version must be 1"),
        (lambda p: p.pop("schema_version"), "schema_version must be 1"),
    ])
    def test_malformed_proposals_exit_two(self, tmp_path, H, mutate, fragment):
        H.write_project(tmp_path)
        proposals = H.base_proposals(self._good_citations(H))
        mutate(proposals)
        code, report, cites, err = H.run_cli(tmp_path, proposals)
        assert code == 2
        assert fragment in err

    def test_missing_files_exit_two(self, tmp_path, H):
        H.write_project(tmp_path)
        proposals = H.base_proposals(self._good_citations(H))
        proposals["sources"]["cl-12345"]["path"] = "sources/nope.md"
        code, _, _, err = H.run_cli(tmp_path, proposals)
        assert code == 2 and "not found" in err

    def test_invalid_json_exit_two(self, tmp_path, H):
        H.write_project(tmp_path)
        scratch = tmp_path / ".cite-check"
        scratch.mkdir(exist_ok=True)
        (scratch / "proposals.json").write_text("{not json", encoding="utf-8")
        import subprocess, sys
        proc = subprocess.run(
            [sys.executable, str(H.SCRIPTS_DIR / "verify_anchors.py"),
             "--proposals", ".cite-check/proposals.json",
             "--out", "cites.json", "--workdir", str(tmp_path)],
            capture_output=True, text=True)
        assert proc.returncode == 2

    def test_pin_passthrough(self, tmp_path, H):
        H.write_project(tmp_path)
        cit = self._good_citations(H)[0]
        cit["pin"] = "461"
        code, _, cites, _ = H.run_cli(tmp_path, H.base_proposals([cit]))
        assert code == 0
        assert cites["citations"][0]["pin"] == "461"


class TestOriginalProvenance:
    """sources[key].original / render_hint (native rendering, cite-check 1.1)."""

    def _proposals_with_original(self, H, original):
        proposals = H.base_proposals([H.citation("c001", quotes=[
            'The "totality of the circumstances" governs our review.'])])
        proposals["sources"]["cl-12345"]["original"] = original
        return proposals

    def test_original_recorded_with_verifier_hash(self, tmp_path, H):
        import hashlib
        H.write_project(tmp_path)
        orig = tmp_path / "sources" / "originals" / "smith.pdf"
        orig.parent.mkdir(parents=True)
        orig.write_bytes(b"%PDF-1.7 fake body")
        code, _, cites, err = H.run_cli(tmp_path, self._proposals_with_original(H, {
            "path": "sources/originals/smith.pdf",
            "media_type": "application/pdf",
            # The proposing model's hash is untrusted and must be replaced.
            "sha256": "0" * 64,
            "pages": 24,
            "extracted_by": "pdftotext -layout + mark_pdf_pages.py",
        }))
        assert code == 0, err
        recorded = cites["sources"]["cl-12345"]["original"]
        assert recorded["sha256"] == hashlib.sha256(orig.read_bytes()).hexdigest()
        assert recorded["bytes"] == orig.stat().st_size
        assert recorded["media_type"] == "application/pdf"
        assert recorded["pages"] == 24
        assert recorded["extracted_by"].startswith("pdftotext")

    def test_original_missing_warns_and_drops(self, tmp_path, H):
        H.write_project(tmp_path)
        code, report, cites, err = H.run_cli(tmp_path, self._proposals_with_original(H, {
            "path": "sources/originals/not_there.pdf",
            "media_type": "application/pdf",
        }))
        assert code == 0, err
        assert "original" not in cites["sources"]["cl-12345"]
        assert any(w["code"] == "original_missing" for w in report["warnings"])

    def test_original_bad_media_type_warns_and_drops(self, tmp_path, H):
        H.write_project(tmp_path)
        orig = tmp_path / "sources" / "originals" / "smith.rtf"
        orig.parent.mkdir(parents=True)
        orig.write_bytes(b"{\\rtf1}")
        code, report, cites, err = H.run_cli(tmp_path, self._proposals_with_original(H, {
            "path": "sources/originals/smith.rtf",
            "media_type": "application/rtf",
        }))
        assert code == 0, err
        assert "original" not in cites["sources"]["cl-12345"]
        assert any(w["code"] == "original_bad_media_type" for w in report["warnings"])

    def test_render_hint_passthrough(self, tmp_path, H):
        H.write_project(tmp_path)
        proposals = H.base_proposals([H.citation("c001", quotes=[
            'The "totality of the circumstances" governs our review.'])])
        proposals["sources"]["cl-12345"]["render_hint"] = "transcript"
        code, _, cites, err = H.run_cli(tmp_path, proposals)
        assert code == 0, err
        assert cites["sources"]["cl-12345"]["render_hint"] == "transcript"
