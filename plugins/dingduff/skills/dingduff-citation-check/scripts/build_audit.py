#!/usr/bin/env python3
"""Audit-log generator for DingDuff cite-check.

Produces a single self-contained, PRINTABLE HTML audit log (letter landscape)
from cites.json (schema v1) and, when present, review.json — the firm-internal
and court-facing record that a human attorney checked the work product.

Columns: citation # · source cited · proposition · successfully anchored? ·
attorney review status (✅ ⚠️ ‼️ ❓) · review note · reviewed by.

Running without --review is valid (all rows ❓ — a "verified but not yet
attorney-reviewed" audit). Every cell is HTML-escaped: notes are free-form
attorney input. An integrity footer records the memo hash, verifier
provenance, and reviewer list for evidentiary value.

Exit codes: 0 success; 2 fatal (missing/malformed inputs).
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_VERSION = "cite-check/build_audit.py 1.0"

# DingDuff brand mark (George), inlined so the audit log is self-contained.
DOG_ICON = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAK5UlEQVR42u1Za4xd11X+1tr7nHPfc2fuPGzPjMfxoxDHhLpp00cQU9EKNagSCshCoEoU/sEfBAIJkFAYCcEPJJDgB/9QQQgJbAT8IIoqWuoQJNo0wg3NpI4dEseveXle99zHOWfvtfhxzr0zE8auHU/aSnj/uNI9d9+t9e31rbW+tQ7waD1a/78XHcAZfG6fc84DAkB/kIHTAe5738s+zJ+fAgJ3pPKEI2qqkMtPdDCZZVL9znPLnTUAWMi36w8ChWgeMBcBBuCnqtXWh44EL4aGz6ZOQUQgUhgitNvZL71yq/0lAGUA6fOALuS0+r4BIAB6uFYbnx7lvyeiMWJlVRw/NVWLjk+WCSCsbKd47foWVHBDgKVSwJVukv3eq9fjfz59GuHiIrKD9IZ9EOOfnKqeaVTtT0yNRc+ExoSqisQJxuqBNKohqSoyVT00WqLI8JwXmdvqZki9+ZknD9fudNP4le+LB54Cgs8D/l+O1v9merT08x8/NZoZa1hFQQT2AhJRhSoREwwTLEO2u07/7Y07GhqySSbbL7+1+RiATRwglfh+Nn0e8AuA9L1s9DLxaabsnJjMqcmckqgqEQgEhQLOKfqZsDVkPv14y7ZqoU8yz/MnR1/+yEzjVwBgfv7hEsh9U+gcYF44Um8+Lv7po6PlH5poRMYYktx3CiIAg0+AQACRAgoYJpQjg/F6aBInUZrJ4x2RmXnAxvHBpNe7ecCcA8xpIDwPeAXGRyvhC6cO1z7z5NG6gsCkQGB4yEKFwjCBibSAAhDQzwRHJ8r4+IlRBSDitX0RcLXawQSyuctzXQR0FfAfOzryh6WQfztxOjrVjLheDpiZcGu9r9++0aZWLUIpYIiqXrrWpo1ORlMjEUQK7xABCiRO+Opyl1XlxOxY+VPra+G/rm4nvYctdPtS6PTh2o+FAQ73E+kFhn+hXrFz4wFrNTRQVQSGEPc93d5M8MSM5PegRGvbKaplA6bdWUIBEJhBh5qRdvrm2HonnUHifu2gY4CeB2gBkHpo/qRRCT7myoI0U6jCf/JU03hVeC8IkRtpmcA0vEK1lijgnDu0C0ROL8bTJ5pYvBnr8na6Ua/VFKvd3ZTF+9FT+3rAWG17FddNvHz42EgwXg9M6hQgKDNR6hXTrTLGGyGiwEBEASipAstbKb62uIYfPlLDVDNC6gRcoEmdwqsSERmgszuV+/PfpQY9EADvYMIS21Yr9BONkOoli8zLIDShClRCg2pk4EWHp8+MlbDWTrGylQz255uLRMUEkOY+YRr+jT48XX+WWBpOrKg6IrJq2bFP7TdeW956+14g9gWQibpqycjTp5pIMsmNIRoIMgKAvG5pkfzzdWa2jlsbfaxuJcPnRAwlqKpC8mcK1QIdTBVoVUvmryphOOEEYLJQBQwHuBMnvw7gL06eBK5eRbofiD0AFgd0JjQNM6uqJ9q5RM3dP8RBSvvmEAFgDSFgRqpuWBpCwxoaJiIaH+HO1lNHR56rR/wH3dSXS9XQ/ehjDTABm3FG33hry1dD+1vPnGx+4j+ubv7yrsvTu6bRcwBdBDBVC1uBQWiYZwLDCCwRlIboBpTYY3zB/9XtRLd7jgLD8CKohAZEgFfVla2EljZ7b96Jsxf//Z30wtFWNF+N7C+O1kIz1QztVCPiyBoeyBNmamSZTB5uRr1mKdhcidO1onbpvoVsAZBzAF+6Gf/Rmyvp73zzf7Zt4ryLLDtmeMPkDcMb5jy9a15xB2X40rUtLN6IiYlwZamDxRsxAksILcMwudfe3cYbt+K/fvV6+wsAFEIuyyR7crYuHzpcg2pOzUpo8YlTo1wvW+0mfmKkFPxpFNBPFhKE7xkD53MQ5gbrlV6GT79+Lf7Ldyv94050eP+9zGO2VcbJqSp6mQxBfPR4E5nP68R3brZxJ87w8uV1qFIRuIxKeU/mrhimwDD5jY7Dt9/dBgBUSxZPTNdwfKJCjci4K8sdYmjvfoNYzwOC5c4KgBUv9b8rtfFRgfYYJGCMQOmZwJqwEhptVCwFhqEKjNcDKEgNE2120lxNUB7MAmJRAame/ZHp+rOh1C46ja+0U/nqWpye7SW+vrKVQEFm1CkpgGY1ADP46kqHne4ve+4m5nQg5M7fav/u7h9mxsrTJ8ZL/7W6nUxcv9PVz56ZoFKVkXkg86oAyDnB8ckKTh6q5TwlaN+J+fK3VjUK7M+GRp97+a3bVQAvAHhBhJbqZWNrJYvU5ZoKBDgVZF7vKdruqUbPA/4cYFbmQaur4IkJyPY75UbihKebJRwZK3SQFHpUi7BmQBRwRS0ggNQDHzk2QtfXe3LrTj/+5GMjX0pTf+HVm/EFdfjVbiJlhfZV8RtNtp+CQNgQ08PK6fOAx8WdS3j6JEidUqNi8NhEFd3M7+1OhsJ64PM8DzMDxybK6DvPG3FaKYf25zYpM2fnaq9/84tb/zS3gLA225iuM61xrv80T9+qqvBK+zdB/IDaSXSrv953zieZInOyUyT+T0GgnbRNADHQSTyOtsr48dMt006cAPjpemj/EwswrbmRZycrwRtKeLabeiWCMQxEAZvIsoFS5UHk9J71PMAXATlzqP6FZjP8zTOzzccPjYRBFHBeEHbbPlBxuyRE/j0XeEQAg6hRtkREZqPropmR0qxh+qxCT8yNl3luokqNspXbGwm9vdy9fqfr/rjbcS+udLKVa9f2jmjuq637Wu4piQJ8rlEOnjs5WRZmQuaFdoq37vKC7nKK7nGQFNuOTVQAJd3sOIXqF4kBgHR2rEKTIyGcU13Z7suV5e7NbjX4s8srnXbBGHnfFFLiOPUiiffiCktCy2p5GKrYVdoKJ+wezlExO4J2U4+p0YjmT7eom4kPLPvPnBmnRsWilwpKEUslshwFPNnqon43QfdAjTWRsiFiS0YMk2ZO6FvXtmmsFujMWIkyrzmhVAdUya9LFUqklGu/QZtWKCmls8caJrQEL4LQEuK+w6V3OsFanP5tL3MXJrPNrQdSo3eNYIBUgV7iqURMUMXbq10AFZobLyF1UCp6mdQJRIHQ8i4maUG23PiBRbOtMlQVfSewHtJOXO/qUmd9s+v+4fWl+B/vxZQHolAARuYFX1lcw5XbHVhmBIZgOE95BJCowhjG69djfP3qZiHDCcXYJfekEu0OlcSJOlHUS8a/uRTzK29tX26n9FOlSvyV94q3hxzu5v1vKWCEhgGiQbLZ2ywAyFSGhSyPjL1pdegLAQJDFPedXl/rYb3jLsQd+XJwe+vyq0B2oNNpEYCJ0KpZRJbRT91OvO5OpgQYInDRdukgm6oOC9tO7lIwE+Kew6V3ttFN/J//91L80nxuG323nvjBChlDpZDQ63GKy7djeC/D0YkWJqrk0dpNPV56Yx23NxJYM/CW4j2fClWACGHIFFWoCgCTGGLHwQEoLpIHClNyWvDOj0MqcUGvzW6aN/Z3ee1ByLs8KoCrivsAX3CQz1tbdaS5VJZCrxAXcywgp47mAC0jnxMVUbwzg8xvXf2AcvlRHlY/MABMqFtL3O77iAvaVALGajvFK1e3IEUJIwLafYdymKfQmxt9bHQdvOjOFHUQxgowA5nzJrKMpJ8FBw7gYlG+M68vxT3HTjTVfEoCBqOTOCz5dGgUAzAGMJxX/jhReL97qEDvyVkKy6TWMPWd3CxUsH6v3lIOg2OPebpP8NwLgn4P3pEpQL///Af71nFh4f6yz6P1aD1a+fpfc31KBCkaNpQAAAAASUVORK5CYII="

# Keep in lockstep with the viewer's verdict model (review_viewer.html) and
# review.schema.json. Legacy values come from pre-round-2 review.json files.
VERDICT_EMOJI = {
    "verified": "✅",
    "needs_attention": "⚠️",
    "rejected": "‼️",
}
LEGACY_VERDICTS = {"misquoted": "rejected", "wrong_pin": "needs_attention"}
UNREVIEWED = "❓"


class FatalError(Exception):
    pass


def _load_json(path: Path, what: str) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FatalError(f"cannot read {what}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise FatalError(f"{what} schema_version must be 1")
    return data


def source_label(src: Dict[str, Any]) -> str:
    """Human label for a source row: case name + reporter cite for opinions,
    official citation (or code § section) for statutes."""
    if src.get("type") == "opinion":
        name = src.get("case_name") or f"cluster {src.get('cluster_id', '?')}"
        cite = src.get("citation")
        return f"{name}, {cite}" if cite else name
    cite = src.get("citation")
    if cite:
        return cite
    code, section = src.get("code"), src.get("section")
    if code and section:
        return f"{code} § {section}"
    return src.get("statute_id") or "unknown statute"


def anchored_label(citation: Dict[str, Any]) -> str:
    status = citation.get("status")
    if status == "anchored":
        matches = {a.get("match") for a in citation.get("anchors", [])}
        kind = "exact" if matches == {"exact"} else "normalized"
        return f"✓ ({kind})"
    if status == "no_quote_claimed":
        return "— no quote claimed"
    reason = citation.get("failure_reason") or "failed"
    if reason == "source_missing":
        return "— source missing"
    return f"✗ {reason.replace('_', ' ')}"


def review_for(citation: Dict[str, Any],
               reviews: Dict[str, Any]) -> Dict[str, str]:
    """Resolve the attorney-review cell set {emoji, note, reviewer} for one
    citation, applying legacy-verdict mapping and binds_to staleness."""
    entry = reviews.get(citation["id"])
    if not isinstance(entry, dict):
        return {"emoji": UNREVIEWED, "note": "", "reviewer": ""}

    verdict = entry.get("verdict", "")
    note = entry.get("note") or ""
    if verdict in LEGACY_VERDICTS:
        note = (note + " " if note else "") + f"[recorded as {verdict}]"
        verdict = LEGACY_VERDICTS[verdict]

    binds = citation.get("binds_to")
    if binds and entry.get("binds_to") and entry["binds_to"] != binds:
        # Stale review: the cite or its proposition changed since the verdict.
        # An audit log must not present it as a live verdict.
        return {
            "emoji": UNREVIEWED,
            "note": "[a prior review of an earlier version of this citation "
                    "was not applied]",
            "reviewer": "",
        }

    emoji = VERDICT_EMOJI.get(verdict)
    if emoji is None:
        return {"emoji": UNREVIEWED, "note": note, "reviewer": ""}
    return {"emoji": emoji, "note": note,
            "reviewer": entry.get("reviewer") or ""}


_PAGE_CSS = """
  @page { size: letter landscape; margin: 0.5in; }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
         font-size: 9.5pt; color: #1a1a1a; background: #fff; margin: 0;
         padding: 12px; }
  @media print { body { padding: 0; } }
  h1 { font-size: 13pt; margin: 0 0 2pt; }
  .meta { color: #555; font-size: 8.5pt; margin-bottom: 8pt; }
  table { width: 100%; border-collapse: collapse; table-layout: fixed; }
  thead { display: table-header-group; }
  th { background: #f0efec; text-align: left; font-size: 8.5pt;
       text-transform: uppercase; letter-spacing: 0.04em; }
  th, td { border: 0.5pt solid #999; padding: 3pt 5pt; vertical-align: top;
           overflow-wrap: break-word; }
  tr { page-break-inside: avoid; }
  td.status { text-align: center; font-size: 12pt; }
  td.anchored { font-size: 8.5pt; }
  .col-id { width: 4%; } .col-src { width: 17%; } .col-prop { width: 28%; }
  .col-anch { width: 10%; } .col-status { width: 6%; } .col-note { width: 25%; }
  .col-by { width: 10%; }
  .integrity { margin-top: 10pt; font-size: 7.5pt; color: #555;
               border-top: 0.5pt solid #999; padding-top: 4pt; }
  .integrity code { font-family: ui-monospace, Menlo, monospace; }
  .legend { font-size: 8pt; color: #555; margin: 4pt 0 8pt; }
"""


def build_audit_html(cites: Dict[str, Any], review: Optional[Dict[str, Any]],
                     title: str) -> str:
    e = html.escape
    reviews = (review or {}).get("reviews", {})
    rows: List[str] = []
    counts = {"✅": 0, "⚠️": 0, "‼️": 0, UNREVIEWED: 0}
    reviewers: List[str] = []

    for c in cites["citations"]:
        src = cites["sources"].get(c["source"], {})
        r = review_for(c, reviews)
        counts[r["emoji"]] += 1
        if r["reviewer"] and r["reviewer"] not in reviewers:
            reviewers.append(r["reviewer"])
        rows.append(
            "<tr>"
            f"<td>{e(c['id'])}</td>"
            f"<td>{e(source_label(src))}</td>"
            f"<td>{e(c.get('proposition', ''))}</td>"
            f"<td class=\"anchored\">{e(anchored_label(c))}</td>"
            f"<td class=\"status\">{e(r['emoji'])}</td>"
            f"<td>{e(r['note'])}</td>"
            f"<td>{e(r['reviewer'])}</td>"
            "</tr>"
        )

    memo = cites["memo"]
    built_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    total = len(cites["citations"])
    reviewed = total - counts[UNREVIEWED]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{e(title)}</title>
<style>{_PAGE_CSS}</style>
</head>
<body>
<h1><img src="{DOG_ICON}" alt="" width="22" height="22" style="vertical-align:-3px;margin-right:7px">{e(title)}</h1>
<div class="meta">Memo: <strong>{e(memo['path'])}</strong> ·
  {reviewed}/{total} citations attorney-reviewed ·
  ✅ {counts['✅']} · ⚠️ {counts['⚠️']} · ‼️ {counts['‼️']} · ❓ {counts[UNREVIEWED]}</div>
<div class="legend">✅ verified · ⚠️ needs attention · ‼️ rejected · ❓ not reviewed.
  "Anchored" = the quoted passage was mechanically located, verbatim, in the
  stored source file by the cite-check verifier.</div>
<table>
<thead><tr>
  <th class="col-id">#</th>
  <th class="col-src">Source cited</th>
  <th class="col-prop">Proposition cited for</th>
  <th class="col-anch">Anchored?</th>
  <th class="col-status">Review</th>
  <th class="col-note">Review note</th>
  <th class="col-by">Reviewed by</th>
</tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
<div class="integrity">
  Integrity record — memo SHA-256: <code>{e(memo['sha256'])}</code> ·
  verification run: {e(memo.get('generated_at', '?'))} by {e(memo.get('generated_by', '?'))} ·
  reviewers: {e(', '.join(reviewers) or '(none)')} ·
  audit generated: {built_at} by {e(SCRIPT_VERSION)}.
  Verdicts bind to each citation's text+proposition hash; a changed citation
  invalidates its prior verdict (shown as ❓).
</div>
</body>
</html>
"""


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cites", required=True, help="path to cites.json")
    parser.add_argument("--review", default=None,
                        help="path to review.json (omit for an unreviewed audit)")
    parser.add_argument("--out", required=True,
                        help="path to write the audit HTML")
    parser.add_argument("--workdir", default=".",
                        help="directory against which relative paths resolve")
    parser.add_argument("--title", default="DingDuff Citation Verification Audit Log")
    args = parser.parse_args(argv)

    workdir = Path(args.workdir)
    try:
        cites = _load_json(workdir / args.cites, "cites.json")
        for key in ("memo", "sources", "citations"):
            if key not in cites:
                raise FatalError(f"cites.json is missing '{key}'")
        review = _load_json(workdir / args.review, "review.json") if args.review else None
    except FatalError as exc:
        print(f"fatal: {exc}", file=sys.stderr)
        return 2

    out_path = workdir / args.out
    out_path.write_text(build_audit_html(cites, review, args.title),
                        encoding="utf-8")
    # Same semantics as the table: stale (binds_to mismatch) and
    # invalid-verdict entries do NOT count as attorney-reviewed.
    reviews = (review or {}).get("reviews", {})
    reviewed = sum(1 for c in cites["citations"]
                   if review_for(c, reviews)["emoji"] != UNREVIEWED)
    print(json.dumps({"ok": True, "out": args.out,
                      "citations": len(cites["citations"]),
                      "reviewed": reviewed}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
