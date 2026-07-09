#!/usr/bin/env python3
"""Form-feed -> `<<pg. N>>` page-marker converter for DingDuff cite-check.

PDF sources are extracted to plain text before verification (e.g. with
`pdftotext -layout file.pdf out.txt`, which delimits pages with form-feed
\\f characters). This script converts those form feeds into the visible
`<<pg. N>>` markers that the cite-check pipeline already understands:
verify_anchors.py and the review viewer both treat the markers as
zero-width during quote matching, and the viewer renders them as page
pills — so the attorney can see real PDF page numbers while checking
pin cites.

Ordering contract (load-bearing): run this BEFORE verify_anchors.py.
cites.json records the marked file's SHA-256, and every anchor offset is
an index into the marked text; inserting markers after verification would
silently shift every anchor. As a guard, input that already contains a
`<<pg. ` token is refused rather than double-marked.

Page numbering: `N` is the 1-based page ordinal by default. When the
document's printed page numbers don't start at 1 (an exhibit excerpt, a
brief with front matter), pass --first-page so the markers carry the
printed numbers the attorney will actually cite.

A marker is emitted at the START of each page's text, on its own line.
Blank pages still get their marker (page count integrity beats prettiness);
a mostly-empty extraction (>30% of pages with no text) is reported to
stderr as a likely scanned/image-only PDF that needs OCR or manual review.

stdout carries one machine-readable JSON report; diagnostics go to stderr.

Exit codes:
    0  converted (report.ok = true)
    2  fatal: unreadable input / not UTF-8 / already contains markers
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

SCRIPT_VERSION = "cite-check/mark_pdf_pages.py 1.0"

# Fraction of empty pages above which the input is probably a scanned PDF
# whose text layer is missing or junk.
EMPTY_PAGE_WARN_RATIO = 0.30


class FatalError(Exception):
    pass


def mark_pages(text: str, first_page: int) -> tuple[str, int, int]:
    """Split on form feeds and prefix each page with `<<pg. N>>\\n`.

    Returns (marked_text, page_count, empty_page_count). A trailing form
    feed (pdftotext emits one after the final page) does not create a
    phantom empty page.
    """
    if "<<pg. " in text:
        raise FatalError(
            "input already contains a '<<pg. ' page marker — refusing to "
            "double-mark. If this file was already processed, use it as-is; "
            "if the document genuinely contains that token, page markers "
            "cannot be added safely.")
    pages = text.split("\f")
    if len(pages) > 1 and pages[-1].strip() == "":
        pages.pop()  # trailing \f after the last page, not a real page
    out_parts: List[str] = []
    empty = 0
    for i, page in enumerate(pages):
        if not page.strip():
            empty += 1
        out_parts.append(f"<<pg. {first_page + i}>>\n{page}")
    return "".join(out_parts), len(pages), empty


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--in", dest="src", required=True,
                        help="form-feed-delimited text (pdftotext output)")
    parser.add_argument("--out", dest="out", required=True,
                        help="path to write the marked text")
    parser.add_argument("--first-page", type=int, default=1,
                        help="printed page number of the first page "
                             "(default 1; use for exhibits/excerpts whose "
                             "printed numbering doesn't start at 1)")
    args = parser.parse_args(argv)

    try:
        try:
            raw = Path(args.src).read_bytes().decode("utf-8")
        except OSError as exc:
            raise FatalError(f"cannot read {args.src}: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise FatalError(f"{args.src} is not valid UTF-8: {exc}") from exc
        marked, page_count, empty_pages = mark_pages(raw, args.first_page)
    except FatalError as exc:
        print(f"fatal: {exc}", file=sys.stderr)
        return 2

    if page_count == 1 and "\f" not in raw:
        print("warning: no form feeds found — the whole input became one "
              "page. Extract with a tool that preserves page breaks "
              "(e.g. `pdftotext -layout`).", file=sys.stderr)
    if page_count and empty_pages / page_count > EMPTY_PAGE_WARN_RATIO:
        print(f"warning: {empty_pages}/{page_count} pages have no text — "
              "this looks like a scanned/image-only PDF. Quotes cannot be "
              "verified against missing text; warn the attorney.",
              file=sys.stderr)

    Path(args.out).write_text(marked, encoding="utf-8", newline="")
    print(json.dumps({
        "ok": True,
        "out": args.out,
        "pages": page_count,
        "empty_pages": empty_pages,
        "first_page": args.first_page,
        "generator": SCRIPT_VERSION,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
