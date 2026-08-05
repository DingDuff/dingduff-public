---
name: "dingduff-validity-check"
description: "Confirm whether a specific case is still good law before an argument rests on it. ALWAYS RUN IN A SUBAGENT (use Opus) — never in the main context window. Subagent will return the valid/invalid finding. Driven by the opinion_verify tool, with a docket check via the PACER tools for federal origins. Use on ANY load-bearing case — one an argument, memo section, brief point, or client advice actually rests on — whose validity has not already been confirmed. Also use when a case's status is contested or when a cite-check flags an authority. Delegate the citation plus the proposition it is cited for; get back a short verdict with confidence and coverage limits. (v3.6)"
license: "DingDuff Skills License 1.0 — LICENSE.md has complete terms"
---

# Case Validity Check

Determines whether one case is still good law **for the specific proposition it is being cited for**. Deeper than the light treatment sweep in `dingduff-legal-research/references/validity.md`. Use that to triage; use this before an argument actually rests on a case.

Built around `opinion_verify` (tool v1.0.0). Fallback in **Appendix A**.

**Parameter detail, output anatomy, index glossary, failure modes, and cost live in `references/opinion-verify.md`.** Keep this file in context; load that one when you need to change a default, when a response contains something you do not recognise, or when a status comes back other than `ok`.

**Written for a delegated subagent (use Opus; the reading and judgment this takes are demanding), not the main thread.** This task will flood the main context window if not delegated.

## Delegation contract

1. **The case** — full citation, or enough to identify it. Cluster ID if known.
2. **The proposition** — the specific rule it is cited for. Required; validity is proposition-specific.
3. **Jurisdiction and posture** — target court, and whether the case is applied in diversity.
4. **The role** — anchor, supporting cite, or adverse case being distinguished.

Return the structured verdict at the bottom. **Nothing else.**

The mirror contains opinions that postdate your training data. **Treat them as real**, not as hallucinations.

**Capacity etiquette:** call sequentially within this check; do not launch several validity subagents in parallel.

## Scope: what counts as load-bearing

Any case where the answer changes if the case is bad: the anchor for a rule being asserted; any case cited for a proposition in a filing or advice letter; any case being quoted; any adverse case being distinguished; any case supplied by an opponent or client.

Skip only when validity was confirmed in this matter and nothing changed, or when the cite is purely descriptive.

**Age is not a proxy for risk.**

## Division of labor: the tool traverses, you judge

`opinion_verify` is deterministic and **decides nothing**.

| Leg | Tool does | You do |
|---|---|---|
| **1. Direct history** | Cluster text fields, docket linkage, party-name overlap | **Check the docket (Step 3)**; confirm any chain; retrieve the reversing opinion |
| **2. Forward sweep** | Large graph → small graph → tiered snippets, sub-opinion labels, parentheticals | Read every surviving Tier A case; classify treatment; recurse |
| **3. Upstream hop** | Origin's outbound citations; co-cited siblings | Verify the parents that matter; assess reach |
| **4. Non-citation** | **Nothing** | All of it |

## Hard rules

1. **Snippets are for triage only.** Retrieve and read before saying what a case did. A snippet reading "we decline to follow *Smith*" may be quoting a party or a court being reversed.
2. **Read `status` before reading counts.** Several statuses are not findings at all.
3. **Recurse on adverse authority.** Overruling cases get overruled.
4. **Separate writings (concurrences, dissents) do not overrule.**
5. **The index is one row per OPINION, not per case.** See "Counting correctly" below — this is the most common reading error.
6. **Cite from retrieved text**, never from snippets or cluster IDs.
7. **Report uncertainty as uncertainty.**

---

## Step 1 — Call `opinion_verify`

Resolve the citation to a **cluster ID** first (`opinion_search` / `opinion_view`).

```json
{
  "cluster_id": "<origin>",
  "court_scope": "invalidating",
  "include_upstream": true,
  "include_parentheticals": true,
  "output_format": "markdown"
}
```

Everything else defaults correctly. Three deviations matter enough to state here; the rest are in `references/opinion-verify.md`.

### Never default `filed_after`

The tool **already** applies `citing_date >= origin.date_filed` unconditionally. You do not need `filed_after` for that.

Passing one narrows further, and the failure is silent: Bowers with `filed_after: 2010-01-01` **misses *Lawrence*** and returns `status: ok`, a plausible graph, zero Tier A, and **no warning**. Overruling has no characteristic distance — *Lawrence* came 17 years after *Bowers*, *Loper Bright* 40 after *Chevron*. No cutoff is safe.

**Two legitimate uses only:** the upstream hop (pass the *origin's* date) and re-verification (pass the prior check's date).

### `additional_courts` is required for Erie

A federal court's construction of state law is displaced by that state's highest court, which sits **nowhere** in the federal chain and will never be admitted by default. Omitting it on a diversity case produces a clean graph that structurally cannot contain the authority most likely to have superseded the origin.

**Texas and Oklahoma each have two courts of last resort** — pass both: `["tex","texcrimapp"]`, `["okla","oklacrimapp"]`. Verify against the **Courts admitted** line, not the case count; an unchanged count may be a true negative.

### Never pass `flag_terms_mode: "replace"`

It discards the 67 curated terms and makes recall a function of your vocabulary. Add doctrine-specific phrasing via `flag_terms` instead — a superseding statute's name, a competing test, a retired standard. Literal phrases, not regexes.

### One note on scope

**For a SCOTUS origin the small graph is `scotus` alone**, because nothing sits above it. Correct, but it means the graph structurally cannot show lower-court erosion — for a SCOTUS origin, Leg 4 is the *only* place erosion can surface. Do not skip it on the strength of a clean graph.

---

## Step 2 — Read `status` first

| `status` | Do this |
|---|---|
| `ok` | Proceed |
| `no_flag_hits` | A distinct finding. **Not "valid."** Go run Leg 4 |
| `small_graph_empty` | **Not "no treatment."** Check whether Erie courts were omitted |
| `no_citers_genuine` | A real zero; CL coverage may still be incomplete |
| `integrity_warning` | **STOP. INDETERMINATE.** |
| `origin_not_found` | May postdate the generation, or you passed an opinion ID. Re-resolve |
| `mirror_unavailable` | **Not a finding.** No API fallback exists by design |
| `mirror_busy` | **Not a finding.** Wait and retry |
| `tool_disabled` | Fall back to Appendix A |

Never collapse any of these into "no adverse treatment."

---

## Step 3 — Check the docket (federal origins)

Direct history — was *this decision* appealed, reversed, vacated, amended, or superseded on reconsideration — is the most common way a lower-court ruling stops being law. The citing graph reaches it only indirectly, and `opinion_verify` reads only sparse cluster fields and party-name overlap. **The docket records it directly, in the clerk's own entries.**

**Do this whenever the origin is a federal district, circuit, or bankruptcy decision.** PACER covers federal courts only — skip it for state origins and say so in the coverage line.

Sequence, cheapest first:

1. **Resolve the docket.** `search_for_pacer_docket` with the case name and `court_id`; add `docket_number` from the opinion's metadata when you have it.
2. **Confirm and orient.** `pacer_docket_view` with `include_entries: false` — metadata only, fast. Check the parties, judge, and terminated date against the opinion so you know you have the right case.
3. **List the orders.** `search_within_pacer_docket` with `document_type: "orders"` and `filed_after` set to the origin's decision date. No text query is needed — the filter works on its own. This is the highest-value call in the sequence: it enumerates everything the court did after the opinion issued.
4. **Target the dispositive entries.** `title_query` for `mandate`, `notice of appeal`, `amended judgment`, `reconsideration`, `vacate`, `remand`.
5. **Follow the appeal.** For an appellate origin, or to learn how an appeal came out, search the reviewing court's own docket — `search_for_pacer_docket` with `court_id` set to the circuit plus the party names.
6. **Before retrieving any PDF**, batch the document IDs through `check_pacer_availability` (up to 300 at once). It reports which documents are actually archived and saves a failed `pacer_document_view`.

What the docket settles that the citing graph cannot: whether an appeal was taken at all; whether the mandate issued and what it said; whether the judgment was amended or vacated on reconsideration **without any published opinion to cite**; whether the case was consolidated or stayed.

**Limits — state these whenever you rely on the docket.**

- Coverage is the RECAP archive, which is crowd-sourced and incomplete. **A missing entry is not evidence that nothing happened.** Older dockets are thin.
- Docket text is the clerk's language, not a holding. "VACATED and REMANDED" gives you the disposition, not its scope — retrieve the opinion before characterizing it.
- A notice of appeal tells you an appeal was filed, not how it came out. Look for the mandate.
- PACER does not cover state courts.

If the docket shows the origin was reversed or vacated, the verdict is settled — retrieve the reviewing court's opinion to confirm and name it, then go to Step 5.

---

## Step 4 — Triage

### Direct history in the tool output

`opinion_verify` reads only cluster text fields and the docket linkage, and **measured on this mirror generation those are almost never populated** — `history` on ~0.5% of clusters, `date_cert_granted` on effectively none. **Its silence is not evidence.** Step 3 is the real check. What the tool *does* find reliably is `same_litigation_candidate` by party-name overlap — treat those as leads to confirm, not findings.

**Direct history means same-litigation appellate treatment only** — was *this opinion* reversed, vacated, or modified on appeal. A later unrelated case overruling the origin is **adverse treatment**, not direct history. Do not put it in the DIRECT HISTORY field.

### Counting correctly

Three kinds of repetition appear in the index, and conflating them inflates your adverse-authority count: **same cluster with different sub-opinions** (*Lawrence* is three rows in Bowers's index, all cluster `130160`); **genuinely duplicate clusters**, which the tool cannot merge (*Georgia v. Public.Resource.Org* under three IDs, *Loper Bright* under two); and **collapsed sub-opinion records**, which the tool does handle and reports.

**Deduplicate by case name before counting or reporting adverse authorities.** Bowers's 35-row index is roughly 24 distinct decisions. Column-by-column detail is in `references/opinion-verify.md`.

### Reading order

Integrity warning → provenance and `content_hash` → graph size, admitted courts, unaudited courts, truncation → index → signal summary → analytics (the **hub** is the likely replacement rule; the **co-cited** list is the doctrinal line Leg 3 needs).

### Tiers

| Tier | Means | Response |
|---|---|---|
| **A** | Flag term near an origin reference in an opinion speaking for the court | **Retrieve and read.** A candidate, not a finding |
| **B** | Flag terms present but not near a reference, or co-occurrence only in a separate writing | Read the snippet; retrieve on real engagement |
| **C** | Cites the origin, no flag terms | Bulk applications; skim for recency |
| **unscanned** | Truncated before scanning | **UNKNOWN**, not clean |

**Tier A is mostly noise, and you should expect that.** Measured on Bowers: 6 Tier A, of which **only *Lawrence* is actual treatment**. *Dobbs* is Tier A because it lists Lawrence-overruling-Bowers in a string cite about overruled cases; *Casey* because the word "overruling" appears near a Bowers reference in a passage about overruling *Roe*; *McDonald* because Scalia discusses stare decisis. A 1-in-6 signal rate is normal. **Zero Tier A does not mean valid** — that is Leg 4's job.

Do not widen `cooccurrence_window` to catch more; it lowers precision far faster than it raises recall.

### Matching treatment to the proposition — read for it

Validity is proposition-specific: a case gutted on one holding may be untouched on another. Nothing in the tool output tells you which holding a citing case engaged, and **page numbers will not tell you either** — CourtListener frequently lacks reporter pagination, so pages are absent from most snippets and unreliable where present. Do not try to filter by page.

**Determine it by reading.** For each Tier A candidate, read the passage around the origin reference and answer three questions:

1. **Is this actually a reference to the origin?** Snippet matching can fire on a party name shared with an unrelated case. Confirm the citation is to your case before going further.
2. **Which of the origin's holdings is the court engaging?** A case abrogating the origin's standing analysis says nothing about its merits holding.
3. **Is the court doing something to the origin, or merely mentioning it?** Inventorying it in a string cite, quoting a party's argument, and reciting history all read like treatment in a snippet and are not.

Never report treatment without having identified which holding it reached.

### Retrieving full text without drowning

Full SCOTUS opinions exceed single-response limits. Do not try to read one straight through. `fetch_opinion_file`, save to disk, then read targeted regions — use the snippet `start`/`end` offsets and the origin's party name to locate the passage that matters. For a shortlist of ambiguous cases, `submit_batch_screen` (≤20 clusters) is cheaper than reading each.

---

## Step 5 — Early exit

**If Step 3 or Leg 2 produces a clear, express reversal, vacatur, or overruling that you have retrieved and read, and it (a) addresses the proposition at issue and (b) comes from a court that binds the target court — the finding is dispositive. Legs 3 and 4 are moot. Say so in the coverage line and stop.**

Still apply the recursion rule: verify the overruling case is itself good law before naming it as the replacement.

Otherwise continue.

---

## Step 6 — Leg 3, the upstream hop

The forward sweep only sees edges that exist. It cannot see the origin relying on a parent that was later killed without anyone telling the origin's citing history.

1. Identify the **3–8 authorities the origin leans on for the proposition** — from the tool's upstream list, ranked by depth.
2. Call `opinion_verify` on each with `filed_after` = **the origin's decision date**. ~150–305 ms each.
3. A parent overruled or limited after the origin relied on it, on the same point, makes the origin **AT RISK** even with a spotless citing history.
4. **Sibling check** from the co-cited list — those cases are the doctrinal line.

---

## Step 7 — Leg 4, the non-citation leg

A graph cannot detect a court that changed the law **without citing anyone in the line**. **The tool does none of this.**

1. **State the current rule independently.** Search the proposition in current doctrinal language, controlling jurisdiction, `-dateFiled`, last ~10 years. Read the recent authoritative statements, then **compare to the origin.** A new element, a shifted burden, a differently-phrased standard, a vanished exception — any is a silent-shift flag.
2. **`show_related_opinions`** for subject-matter neighbors that never cite the origin.
3. **Statutory supersession** — `codes_search`, check effective dates. A statutory amendment can abrogate a line while citing nothing.
4. **Doctrinal resets** — intervening en banc, state high court, or constitutional decision, named or not.

---

## Step 8 — Verdict

**VALID** · **VALID BUT NARROWED** · **AT RISK** · **QUESTIONED** · **INVALID FOR THIS PROPOSITION** · **INVALID** · **INDETERMINATE**

Always qualified by the proposition. Name the replacement whenever the case is unusable.

| Cap confidence at | When |
|---|---|
| **INDETERMINATE** | `integrity_warning`; `origin_not_found`; origin has no text |
| **Low** | API supplement failed or skipped; truncation with Tier A dropped |
| **Moderate** | `api_truncated`; unaudited courts in the graph; Leg 4 inconclusive; adverse cases screened but not read; federal origin whose docket could not be checked |
| **High** | Full coverage, every surviving Tier A read, Leg 4 run and consistent — **or** an express reversal or overruling retrieved and verified under Step 5 |

**Unaudited courts.** 3,330 courts in the hierarchy, **205 human-audited**; the state intermediate appellate layer is largely unaudited. The tool names them — pass that through.

---

## Return to the caller

Roughly 250 words. Structured, quoting the operative language, no traversal narrative.

```
CASE: <full citation>
PROPOSITION CHECKED: <the rule>
JURISDICTION: <target court>

STATUS: <one of the seven> — confidence <high/moderate/low>

DIRECT HISTORY (same litigation only): <reversal/vacatur/amendment chain. Say whether
the docket was checked and what it showed, or why it could not be (state origin, no
RECAP coverage).>

ADVERSE TREATMENT: <each: citing case, full cite, the operative language quoted, and
which of the origin's holdings it reached. DEDUPLICATED BY CASE NAME. Or "none located.">

AT-RISK FINDINGS: <upstream authority undermined after this case relied on it, or
divergence between this case and the current rule. Or "none.">

RECENT APPLICATION: <most recent case applying it for this proposition — or the silence>

IF UNUSABLE — WHAT REPLACES IT: <case or statute now stating the rule, with cite and
operative language. The graph hub is usually the candidate.>

COVERAGE: <small graph size and distinct-case count; courts admitted; mirror generation
and watermark; API supplement status; truncation/unscanned; unaudited courts; docket
check status; content_hash. Say which legs ran and which were moot under Step 5. State
that silent overruling — a court changing the rule without citing this case or its line —
is outside the reach of any citation-graph method.>
```

Most of the coverage line is copied from provenance rather than composed. A verdict without a stated boundary invites more reliance than the method can bear.

---

## Worked example

> *Smith v. Acme*, 900 F.3d 100 (5th Cir. 2018), cited for presumptive enforceability of a
> forum-selection clause in an employment contract under Texas law. Diversity; brief headed
> for N.D. Tex.

1. Resolve to a cluster ID. Call with `include_upstream: true` and, because this is Erie, `additional_courts: ["tex","texcrimapp"]`. Confirm all four courts in *Courts admitted*.
2. `status: ok`; no integrity warning; 41 rows, no truncation; **5 Tier A**.
3. Federal origin, so check the docket: resolve it in `ca5`, then `search_within_pacer_docket` with `document_type: "orders"` and `filed_after` the opinion date. Panel rehearing denied, no en banc, mandate issued. No direct history.
4. Deduplicate: 5 rows are 3 distinct decisions (one appears as combined + dissent).
5. One is a dissent — note as pressure, not treatment. Two remain. Retrieve both and read the region around the snippet offsets.
6. The first engages *Smith* only on personal jurisdiction — a different holding. Set aside. The second, a 2023 `ca5` panel (depth 7, out-degree 5, term *"to the extent that"*), engages the enforceability holding directly and narrows it to at-will employment, reserving fixed-term contracts.
7. Not an express overruling — **no early exit**. Continue.
8. Upstream: a 2011 Texas Supreme Court case, `filed_after` = *Smith*'s date → clean. Top sibling → clean.
9. Leg 4: recent Texas authority is consistent with *Smith* as narrowed.
10. **VALID BUT NARROWED** — confined to at-will employment — confidence high.

---

## Appendix A — fallback when `opinion_verify` is unavailable

Applies on `tool_disabled` or in an environment without the tool. (`mirror_unavailable` and `mirror_busy` are **not** cues to fall back.) Step 3's docket check is unaffected — run it regardless.

```json
{"identifier": "<cite or cluster_id>", "order_by": "-dateFiled", "limit_results": 50}
{"identifier": "<cite or cluster_id>", "order_by": "-citeCount", "limit_results": 50}
{"identifier": "<cite or cluster_id>", "court_ids": "<invalidating courts>", "limit_results": 50, "order_by": "-dateFiled"}
```

**Do not skip `-citeCount`** — the overruling case may sit far below the date-ordered horizon while being the most-cited in the line. Filter to courts that could invalidate; `court_types: "F"` is not state-scoped, so name circuits explicitly (`ca5`). Cross-check in `opinion_search`:

```
"<case name>" AND (overruled OR abrogated OR "no longer good law" OR "we disapprove" OR
"receded from" OR "declined to follow" OR "superseded by statute" OR "limited to its facts" OR
"called into question" OR "we now hold" OR "to the extent that")
```

Classify with the traditional codes, each tied to a point of law: **o** overruled · **L** limited · **q** questioned · **c** criticized · **d** distinguished · **e** explained · **f** followed · **h** harmonized · **j** cited in dissent. Legs 3 and 4 unchanged. A result of 0 is not proof a case is uncited. Confidence caps at **moderate**.

---

## Standing limits — state these in every verdict

1. Cannot detect silent overruling by a court that never cites the origin or its line.
2. Cannot detect statutory supersession unless a citing opinion says so.
3. Flag-term recall is bounded by the 67-term list.
4. Cannot distinguish holding from dictum, argument, or quotation.
5. Inherits every CourtListener gap: thin state appellate coverage, unpublished dispositions, eyecite failures, unreported orders.
6. CourtListener frequently lacks reporter pagination, so a pinpoint page often cannot be produced from tool output at all.
7. `opinion_verify`'s own direct-history detection is near-blind on this mirror generation; the docket check in Step 3 is the real one.
8. Docket coverage is the RECAP archive — crowd-sourced, incomplete, federal only. A missing entry is not evidence.
9. Erie and certified-question authority requires `additional_courts`.
10. **A zero result is never proof of validity.**

---

## Related skills

Called by `dingduff-legal-research`, `dingduff-legal-analysis`, `dingduff-legal-writing`, and `dingduff-citation-check`. Note the capacity ceiling: a 20-citation cite-check is ~160 tool calls and ~2 minutes occupying both admission slots — do not run two at once. Citation *form* is `dingduff-legal-citation-format`; this skill checks whether a case **is** good law, not whether the cite **looks** right.

