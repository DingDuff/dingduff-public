# Fallback — validity checking without `opinion_verify`

Everything the tool did for you, done by hand. The judgment steps in SKILL.md are unchanged; what changes is that you now assemble the evidence yourself, and you lose the signals that made triage cheap.

## When this applies

| Condition | Action |
|---|---|
| `tool_disabled`, or an environment without the tool | **Use this file** |
| `mirror_unavailable` | **Wait and retry.** Not a cue to fall back — there is no API substitute for the mirror by design |
| `mirror_busy` | **Wait and retry.** Capacity, not failure |
| `integrity_warning` | **Stop. INDETERMINATE.** Falling back does not cure it |

**Step 3's docket check is unaffected — run it exactly as written.** It uses the PACER tools, not `opinion_verify`, and for a federal origin it remains the strongest evidence of direct history.

## What you lose, and what replaces it

| The tool gave you | Without it |
|---|---|
| Court-scoped graph (`court_scope: "invalidating"`) | Construct the invalidating court set yourself — see below |
| Tier A/B/C ranking | Every citer arrives unranked. Triage by reading snippets |
| Flag-term co-occurrence | The boolean search in F3 is the substitute, and it is coarser |
| Curated 67-term flag list | Your search vocabulary. Use the list in F3 verbatim rather than improvising |
| Upstream authority list | Read the origin and extract what it relies on yourself |
| Co-cited siblings | `show_related_opinions` |
| Graph hub (likely replacement rule) | No substitute. Identify the current rule by reading recent authority — Leg 4 |
| Truncation and coverage reporting | You will not be told what you did not see. Say so in the verdict |
| Sub-opinion collapsing | Deduplicate by hand — see F4 |

Because the tool reported its own blind spots and this route does not, **the confidence cap is `moderate` regardless of how clean the result looks.**

---

## F1 — Scope the courts

Decide which courts could actually invalidate the origin before you search, or you will drown in bulk applications.

That set is: the origin's own court, the appellate chain above it, and the Supreme Court. For a state origin applying its own law, add nothing. **For a federal court applying state law under *Erie*, add that state's highest court** — it sits nowhere in the federal chain and is the authority most likely to have superseded the origin. **Texas and Oklahoma each have two courts of last resort** (`tex` + `texcrimapp`; `okla` + `oklacrimapp`).

Two `show_citing_opinions` traps:

- `court_types: "F"` is **not state-scoped**. Combining `states` with `"F"` returns no circuits at all. Name the circuit explicitly with `court_ids` — `ca5` for a Texas federal origin.
- `states` alone pulls in state supreme, state appellate, and federal district courts for that state. Useful for a wide first pass, too broad for a targeted one.

## F2 — Forward sweep

Three calls. They return overlapping but different sets; run all three.

```json
{"identifier": "<cite or cluster_id>", "order_by": "-dateFiled", "limit_results": 50}
{"identifier": "<cite or cluster_id>", "order_by": "-citeCount", "limit_results": 50}
{"identifier": "<cite or cluster_id>", "court_ids": "<invalidating courts>", "limit_results": 50, "order_by": "-dateFiled"}
```

The first catches recent treatment. The second is the one people skip and should not: **an overruling decision may sit far below the date-ordered horizon while being the most-cited case in the line.** The third concentrates on courts that can actually do damage.

Raise `limit_results` (max 500) when a case is heavily cited; each 20 results costs roughly one API request.

**A zero result is not proof a case is uncited.** The response carries a warning when CourtListener's own metadata suggests citations exist that the citator did not return — read for it.

## F3 — Word searches

Run these **regardless of what F2 returned.** The citation graph and full-text search miss different cases, and neither alone is complete coverage. This is not a fallback-only rule; it applies in the main flow too.

```
"<case name>"
"<citation string>"
```

Then the flag-term sweep, which stands in for the co-occurrence detection you no longer have:

```
"<case name>" AND (overruled OR abrogated OR "no longer good law" OR "we disapprove" OR
"receded from" OR "declined to follow" OR "superseded by statute" OR "limited to its facts" OR
"called into question" OR "we now hold" OR "to the extent that")
```

Add doctrine-specific phrasing where you have it — the name of a superseding statute, a competing test, a standard being retired. Literal phrases, not regexes.

The plain name search is the widest of the three: it catches courts citing the origin by short form, by docket number, or by Westlaw number, none of which a citation-string search can reach.

## F4 — Deduplicate, then triage

**Deduplicate by case name before counting anything.** Without the tool's sub-opinion collapsing you will see the same decision more than once — as separate lead and dissenting opinions, as duplicate clusters CourtListener never merged, and again across the F2 and F3 routes. An inflated adverse-authority count is the most common error on this path.

Then triage as you would Tier A output. For each candidate, read the passage around the origin reference and answer the three questions from SKILL.md Step 4: is this actually a reference to the origin; which of the origin's holdings is the court engaging; is the court doing something to the origin or merely mentioning it. String cites, quoted party arguments, and recited history all look like treatment in a snippet and are not.

**Snippets remain triage only.** Retrieve and read before characterizing what any case did.

## F5 — Legs 3 and 4

Both still run, and Leg 3 is harder here because you have no upstream list.

**Leg 3 — upstream.** Read the origin and identify the three to eight authorities it actually leans on *for the proposition being checked*, not everything it cites. Check each for later overruling or limitation, using this same fallback method. A parent killed after the origin relied on it puts the origin **AT RISK** even with a spotless citing history. Then `show_related_opinions` for the doctrinal siblings.

**Leg 4 — non-citation.** Unchanged, and it carries more weight than usual now. State the current rule independently: search the proposition in current doctrinal language, in the controlling jurisdiction, ordered by `-dateFiled`, over the last decade or so. Read the recent authoritative statements and compare them to the origin. A new element, a shifted burden, a rephrased standard, a vanished exception — any is a silent-shift flag. Check `codes_search` for statutory supersession and its effective dates; a statute can abrogate a line while citing nothing.

## Classifying

Traditional codes, each tied to a specific point of law rather than the case as a whole:

**o** overruled · **L** limited · **q** questioned · **c** criticized · **d** distinguished · **e** explained · **f** followed · **h** harmonized · **j** cited in dissent

Separate writings do not overrule. Recurse on adverse authority — the case that overruled yours may itself have been overruled.

## What to say in the verdict

Report the verdict in the standard format from SKILL.md, with three additions to the coverage line:

- That `opinion_verify` was unavailable and this route was used instead.
- Which routes produced the citing results — F2, F3, or both.
- That tiering, co-occurrence detection, and truncation reporting were unavailable, so the completeness of the sweep is unmeasured.

**Confidence caps at `moderate`.**
