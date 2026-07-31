# `opinion_verify` — tool reference

Operating manual for the tool. Load this when you need to change a parameter from the default call, when a response contains something you do not recognise, or when a check comes back with a status other than `ok`. The default call in SKILL.md is correct for most checks and you do not need this file to run one.

Tool version 1.0.0. Every measured number below is from staging against the 2026-06-30 mirror generation.

**One thing no parameter can change:** the tool reads a citation graph. Nothing you pass it will make it detect a court that changed the law without citing the origin or its line, or a statute that abrogated it silently. That is Leg 4's job and it stays yours.

---

## 1. The default call

```json
{
  "cluster_id": "<origin>",
  "court_scope": "invalidating",
  "include_upstream": true,
  "include_parentheticals": true,
  "output_format": "markdown"
}
```

Everything else defaults sensibly. The sections below are ordered by how much damage a wrong value does — read §2 before you deviate from the defaults at all.

---

## 2. Parameters that can produce a confidently wrong answer

### `filed_after` — the sharpest edge in the tool

ISO date, `YYYY-MM-DD`. Default null. **Leave it null on a first check.**

The tool *already* applies `citing_date >= origin.date_filed` unconditionally, on every query shape. A case decided before the origin cannot invalidate it, and there is no parameter to disable that. So you never need `filed_after` merely to exclude earlier cases.

What it does instead is narrow *further*, and the failure mode is silent. Measured, on cases whose overruling is public record (`OK`/`MISS` = whether the overruling case survived into the small graph; `/n` = resulting graph size):

| Origin | Overruled by | none | 2000-01-01 | 2010-01-01 | 2016-01-01 | 2020-01-01 |
|---|---|---|---|---|---|---|
| Bowers v. Hardwick | *Lawrence* 2003 | OK/35 | OK/15 | **MISS**/10 | **MISS**/6 | **MISS**/6 |
| Austin v. Mich. Chamber | *Citizens United* 2010 | OK/28 | OK/19 | OK/9 | **MISS**/6 | **MISS**/5 |
| Chevron v. NRDC | *Loper Bright* 2024 | OK/396 | OK/219 | OK/105 | OK/52 | OK/26 |
| Roe v. Wade | *Dobbs* 2022 | OK/220 | OK/50 | OK/34 | OK/29 | OK/18 |

A missed overruling returns `status: "ok"`, a plausible small graph, zero Tier A, and **no warning of any kind**. There is no signal distinguishing it from a genuinely clean case.

Overruling has no characteristic distance — *Lawrence* came 17 years after *Bowers*, *Loper Bright* 40 years after *Chevron*. No cutoff is safe.

**The only two legitimate uses:**

| Use | Pass | Why it is safe |
|---|---|---|
| Upstream hop | the **origin's** `date_filed` | You are asking whether a parent was harmed *after* the origin leaned on it. Earlier treatment is irrelevant by construction |
| Re-verification | the date of the **prior check** | You already have complete coverage up to that date |

### `additional_courts` — required for Erie, silent when omitted

Array of CourtListener court IDs. Default empty.

A federal court's construction of state law is displaced when that state's highest court decides the question — and that court sits **nowhere** in the federal appellate chain, so `court_scope: "invalidating"` will never admit it. Omitting this on a diversity case produces a clean-looking graph that structurally cannot contain the authority most likely to have superseded the origin.

Measured: *Roe* admits only `scotus` by default and returns **220** cases. With `["tex","cal","ny"]` it admits all four courts and returns **324**.

**Bifurcated states.** Texas and Oklahoma each have two courts of last resort, split civil/criminal. Pass both — the tool cannot infer subject matter:

```json
"additional_courts": ["tex", "texcrimapp"]
"additional_courts": ["okla", "oklacrimapp"]
```

**Verifying it took effect.** Identical results before and after adding courts does not mean the parameter failed. Measured: *Broussard* with `["tex","texcrimapp"]` returns exactly the same 373 cases, because no Texas court cites it — a true negative. Check the **Courts admitted** line in the Graph section, not the case count.

Also pass this for a certified-question posture, and any time the origin's reasoning turns on a body of law whose authoritative expositor is outside its own hierarchy.

### `max_cases` — truncation is not harmless

Integer, 1–1500. Default **400**.

Caps the number of cases whose *text* is scanned. The index still covers the entire small graph; cases past the cap come back `tier: "unscanned"`, which means **unknown**, not "no flag terms."

The default is calibrated against real small-graph sizes:

| Population | n | median | p75 | p90 | max |
|---|---|---|---|---|---|
| ordinary origins (≥5 citations) | 120 | 10 | 23 | 44 | 114 |
| heavily cited (≥300 citations) | 60 | 260 | 476 | 804 | 10,172 |

So 400 covers essentially every ordinary case and roughly the 70th percentile of heavily-cited ones.

Why raising it matters when coverage reports truncation: the pre-text ordering (court authority → en banc → speaks-for-the-court → depth → recency) **cannot know which cases carry flag terms until it reads them**. Measured on *Broussard*: **16 Tier A at a cap of 150, 28 at 400.** Twelve Tier A cases were sitting below an arbitrary line.

If the coverage note reports truncation on a case you actually care about, raise the cap and re-run. Cost is roughly linear in cases scanned.

### `flag_terms_mode` — never `replace`

Enum `augment` | `replace`. Default `augment`. **Leave it.**

`replace` discards the 67 curated terms and uses only yours, which makes recall a function of your vocabulary on the day you called. The curated list carries regional and idiomatic phrasing you will not think to supply — *"we recede from"* (Florida), *"we disapprove of"* (California), *"is no longer viable after"*, *"we now hold"*, *"to the extent that"*.

### `flag_terms`

Array of strings. Default empty. **Matched as literal phrases, not regexes.** Case-insensitive.

Add only doctrine-specific phrasing the curated list cannot know about:

- the name of a statute that may have superseded the origin
- a competing test by name — "the *Lemon* test", "the *Chevron* framework"
- a standard being retired, in the words courts use for it
- a term of art unique to the doctrine

Do not add generic negative words. They are already there, and every added term widens the co-occurrence net and therefore the false-positive rate.

---

## 3. Parameters that shape scope

### `cluster_id`

String, required. A CourtListener **cluster** ID — not an opinion ID. Resolve a citation with `opinion_search` or `opinion_view` first.

If you pass an opinion ID you will usually get `origin_not_found`, which is also what you get for a case that postdates the mirror generation. Distinguish them by re-resolving the citation.

The tool expands the cluster to **all** of its opinions before joining the citation graph, so citers recorded against a concurrence or dissent are included. The Origin block reports the expansion — Bowers, for example, is 6 opinions (`010combined`, `020lead`, 2× `030concurrence`, 2× `040dissent`).

### `court_scope`

Enum. Default `invalidating`.

| Value | Admits | Use when |
|---|---|---|
| `invalidating` | The origin's own court, its appellate chain, SCOTUS | Always, unless below |
| `invalidating_plus_peer` | Adds sister circuits and sister state appellate districts | A split is suspected, or the caller asked about one |
| `all` | No court filter | Almost never — see below |

Peer courts come back marked `can_invalidate: false` and ranked below the invalidating set. **Their disagreement is a split, not invalidity.** A sister circuit "declining to follow" the origin does not impair it and must never be reported as though it did. Measured on *Broussard*: 376 cases, 3 marked cannot-invalidate.

`all` is bounded by a server-side citer cap **and disables the API supplement**, so it is both incomplete and stale. It exists for exploration, not verification.

**For a SCOTUS origin, `invalidating` resolves to `scotus` alone**, because nothing sits above it. That is correct, and it means the graph structurally cannot show lower-court erosion. For a SCOTUS origin, Leg 4 is the only place erosion can surface — do not skip it on the strength of a clean graph.

### `exclude_courts`

Array of court IDs. Default empty. Suppresses courts from the graph.

Rarely appropriate in a validity check — you are excluding courts that by definition could invalidate the origin. Legitimate uses are narrow: re-running a very large graph while deliberately setting aside a court you have already examined in full. Anything you exclude belongs in your coverage note.

### `tiers`

Array from `["A","B","C"]`. Default null (all).

Restricts which tiers get **snippets**. The index always covers every case regardless. `["A"]` on a large graph is a reasonable way to cut response size when you already know you will only read Tier A — but you lose the ability to spot a Tier B case whose snippet reveals real engagement, so prefer raising `max_cases` over narrowing tiers.

### `include_upstream`

Boolean. Default false. **Pass `true` always.**

Returns the authorities the origin itself cites, deepest first, with `depth` and cluster IDs. This is the input to Leg 3, it is free, and obtaining it any other way costs a full retrieval and read of the origin.

Bowers returns 60 upstream authorities, top of list: *Stanley v. Georgia* (depth 40), *Griswold* (26), *Carey* (20), *Loving* (17). Depth is your ranking signal for which parents actually carry weight.

---

## 4. Parameters that shape the text

### `cooccurrence_window`

Integer characters, 50–4000. Default **500**.

The distance between a flag term and a reference to the origin at which the pair counts as a co-occurrence hit — which is what promotes a case to Tier A. This is the single knob controlling the tool's signal-to-noise ratio.

**Widening it raises recall and lowers precision, fast.** At the default, Bowers already returns 6 Tier A of which only *Lawrence* is real treatment: *Casey* fires because "overruling" appears within 500 characters of a Bowers footnote reference, in a passage about overruling *Roe*. Widening to 2000 would pull in far more of that.

**Narrowing it** (200–300) is occasionally useful on a very large graph where Tier A is unmanageable and you want only tight, unambiguous pairings. You will miss treatment expressed at a distance — a court that discusses the origin for a paragraph and then announces the overruling.

Change this deliberately or not at all, and say so in your coverage note if you do.

### `snippet_size`

Integer **words**, 30–400. Default 150. Snapped to sentence boundaries.

Raise it when snippets are cutting off mid-argument and you cannot tell whether the court is speaking or characterising a party's position. Lower it when a large Tier A set is producing an unreadable response and you only need to identify which cases warrant retrieval.

Sentence-snapping means you never get a mid-sentence cut, which matters: attribution cues live at sentence starts — *"Appellant contends that…"*, *"The dissent would…"*.

### `snippet_merge_gap`

Integer **characters**, 0–2000. Default 200. Snippets closer together than this merge into one.

Raising it produces fewer, longer, more readable passages at the cost of pulling in intervening text. Lowering it fragments. Rarely worth touching.

### `include_parentheticals`

Boolean. Default true. **Leave it on.**

Attaches court-written "holding that…" summaries of the origin, drawn from CourtListener's parenthetical data and already filtered through its junk blocklist. This is the closest thing in the corpus to a Shepard's editorial squib and it is far denser per token than a raw snippet.

Coverage is only ~9–23% of citers depending on how heavily cited the origin is. **They are enrichment on cases already in the graph** — they never build or bound the case list, and a case without one was still examined. Verify against opinion text before quoting one.

---

## 5. Parameters that shape transport

### `output_format`

Enum `markdown` | `json`. Default markdown. **Use markdown.**

The markdown layer is written to be read and is the richer surface. The JSON `currency` field is a prose sentence anyway, so whether the API supplement ran is only readable as English in either format.

Reach for JSON only when you are doing something programmatic across many cases — and note §8 on `origin_pincites` before you do.

### `refresh_api`

Boolean. Default true. **Leave it on.**

Controls the supplemental CourtListener call covering the window since the mirror generation, filtered to the same court set. Turning it off leaves results current only through the watermark — which on a quarterly export is up to four months stale by quarter's end.

If it is off, or if it failed, that fact belongs in your coverage note and caps your confidence at **low**.

---

## 6. Full parameter table

| Parameter | Type | Default | Bounds |
|---|---|---|---|
| `cluster_id` | string | *required* | CourtListener cluster ID |
| `flag_terms` | string[] | `[]` | Literal phrases |
| `flag_terms_mode` | enum | `augment` | `augment` \| `replace` |
| `court_scope` | enum | `invalidating` | `invalidating` \| `invalidating_plus_peer` \| `all` |
| `additional_courts` | string[] | `[]` | Court IDs |
| `exclude_courts` | string[] | `[]` | Court IDs |
| `filed_after` | date | null | `YYYY-MM-DD` |
| `snippet_size` | int (words) | 150 | 30–400 |
| `snippet_merge_gap` | int (chars) | 200 | 0–2000 |
| `cooccurrence_window` | int (chars) | 500 | 50–4000 |
| `tiers` | string[] | all | subset of `A`,`B`,`C` |
| `max_cases` | int | 400 | 1–1500 |
| `include_upstream` | bool | false | |
| `include_parentheticals` | bool | true | |
| `refresh_api` | bool | true | |
| `output_format` | enum | `markdown` | `markdown` \| `json` |

---

## 7. Anatomy of the response

The envelope carries `success`, `status`, `content_hash`, `report` (the markdown), and `download` when the snippet body exceeds ~15,000 characters. Under that threshold the body is inlined and there is no download link.

`content_hash` identifies the exact verification run — same inputs, same mirror generation, same version stamps produce a byte-identical report and the same hash. Record it in your coverage line; a cite-check record can reference it.

The markdown report, in order:

| Section | What it is for |
|---|---|
| **Header disclaimer** | States the tool does not determine validity. Not decorative — it is the contract |
| **Origin** | Identity, `citation_count`, and the cluster expansion (how many opinions were joined) |
| **⚠ Data-integrity warning** | Present only when the mirror's citer count is materially below CourtListener's own. **Stop if you see it** |
| **Status** | With prose explanation. See §9 |
| **Provenance** | Mirror generation, watermark, version stamps, tool version, and the currency sentence from the API supplement. Most of your coverage line comes from here |
| **Graph** | Large graph size, small graph size, tier counts, counts by court, **courts admitted**, unaudited courts |
| **Direct history** | Same-litigation treatment — but read the caveat printed beneath it |
| **Analytics** | Hub, top co-cited, upstream authorities, last known treatment |
| **Index** | One row per **opinion** in the small graph |
| **Signal summary** | Strongest co-occurrence snippet per Tier A case, verbatim, capped at 10 |
| **Coverage limits** | Duplicate collapses, truncation, cache notes |
| **Snippet body** | Inline or a 1-hour download link |

### Reading Analytics

- **Graph hub** — the small-graph case cited by the most *other* small-graph cases. Usually the modern restatement of the rule, and usually the answer to "what replaces it" if the origin is bad.
- **Top co-cited** — cases most often cited *alongside* the origin. This is the origin's doctrinal line, and it is what the sibling check in Leg 3 runs on. Adverse treatment of a sibling on the shared proposition exposes the origin even when its own citing history is clean.
- **Upstream authorities** — what the origin cites, deepest first. Leg 3's input.
- **Last known treatment** — the most recent small-graph case. A long silence in an active area is itself a signal.

### The Direct history caveat

The tool reads only cluster text fields and the docket. On this mirror generation `history` is populated on ~0.5% of clusters and `date_cert_granted` on effectively none. **Its silence is not evidence.** The section will print "No same-litigation history was found" — that is a statement about the fields, not about the case. Report that the check was not meaningfully available rather than reporting a negative finding.

---

## 8. Index column glossary

| Column | Meaning |
|---|---|
| **Tier** | `A` / `B` / `C` / `unscanned` — see SKILL.md |
| **Case** | Name. **Not unique** — see below |
| **Court** | CourtListener court ID |
| **Filed** | Decision date |
| **cluster_id** | Use for retrieval |
| **Type** | `010combined`, `020lead`, `030concurrence`, `040dissent`, `035concurrenceinpart`, `070rehearing`, `100trialcourt` |
| **Inval** | `can_invalidate` — `N` marks a peer court |
| **En banc** | Detected by name match or panel size |
| **Depth** | How many times the citing opinion cites the origin. High depth means substantive engagement, not a string cite |
| **Flags** | Count of flag-term hits anywhere in the opinion |
| **Refs** | Count of references to the origin |
| **Co-occ** | Whether any flag term fell within the window of a reference. This is what makes Tier A |
| **Paren** | Whether a court-written parenthetical about the origin exists |

**Three kinds of repetition, and you must not conflate them:**

1. **Same cluster, different sub-opinions.** One decision, several rows. *Lawrence* appears three times in Bowers's index — combined, dissent, concurrence — all cluster `130160`.
2. **Genuinely duplicate clusters.** CourtListener holds some decisions under two or three cluster IDs. *Georgia v. Public.Resource.Org* appears at `4748670`, `4749014`, and `4749015`. *Loper Bright* appears twice in Chevron's Tier A. The tool cannot merge these.
3. **Collapsed sub-opinion records** — the tool *does* handle these and reports the count in Coverage limits (9 collapsed on Bowers).

**Deduplicate by case name before counting adverse authorities.** Bowers's 35-row index is roughly 24 distinct decisions.

### On `opinion_type` and who speaks for the court

`020lead` is **not** the majority test. Sampled distribution across the corpus:

```
020lead 45% · 010combined 33% · 100trialcourt 6% · 040dissent 1.6%
030concurrence 1.3% · 070rehearing 0.4% · 035concurrenceinpart 0.3%
```

`010combined` is a third of the corpus and **is** the court's opinion in those records — it is what CourtListener uses when a case was ingested as one undifferentiated document. Treating only `020lead` as authoritative silently demotes a third of all citing opinions. The markdown signal summary resolves this for you, labelling each snippet in plain language ("combined (the court's opinion)"); JSON exposes it as `speaks_for_the_court`.

### JSON-only fields

If you call with `output_format: "json"`, each entry in `cases` additionally carries `speaks_for_the_court`, `is_peer_court`, `court_audited`, `subject_matter_limit`, `text_scanned`, `terms`, `intra_graph_out_degree` / `_in_degree`, `parentheticals`, `text_error`, and `snippets[]` with `category`, `terms`, `page`, `start`, `end`, `reference_confidence`, `text`.

`reference_confidence` is `anchor` (CourtListener's own citation markup — most reliable), `id_chain` (an `Id.` resolved back to a preceding anchor), or `name_match` (party-name match only — **produces false positives**; a shared surname is enough to fire it).

`start` / `end` are character offsets into the tool's normalised text. They are useful for locating a passage inside a retrieved opinion.

> **`origin_pincites` and `has_star_pagination`: do not act on these.** They purport to give the pages of the origin a citing court relied on. CourtListener frequently lacks reporter pagination, so these are absent on most cases and unreliable where present — filtering a Tier A set by page will discard real treatment more often than it saves you a read. Determine which holding a citing case engaged by **reading the passage**, per SKILL.md.

---

## 9. Status vocabulary

Nine values. Several are not findings at all. **Never collapse any of them into "no adverse treatment."**

| `status` | Meaning | Action |
|---|---|---|
| `ok` | Graph built, flag hits present | Triage |
| `no_flag_hits` | Small graph populated, zero flag terms anywhere | A distinct finding. **Not "valid"** — term matching cannot see silent narrowing. Run Leg 4 |
| `small_graph_empty` | Citers exist, none from a court that could invalidate | **Not "no treatment."** First check whether Erie courts were wrongly omitted |
| `no_citers_genuine` | Zero citers **and** `citation_count` is 0 | A real zero. CourtListener coverage may still be incomplete |
| `integrity_warning` | Mirror citers < 50% of CourtListener's `citation_count` | **STOP.** Return INDETERMINATE. Do not reason around it |
| `origin_not_found` | Cluster not in the mirror | Postdates the generation, or you passed an opinion ID. Re-resolve |
| `mirror_unavailable` | Mirror down or disabled | **Not a finding.** No API fallback exists by design |
| `mirror_busy` | Admission control refused | **Not a finding.** Wait and retry. Do not fall back |
| `tool_disabled` | Kill switch | Fall back to Appendix A of SKILL.md |

`integrity_warning` exists because a false "no citing opinions" is the most dangerous output this tool can produce, and a 77.5-million-row citation load is exactly the kind of thing that can go partially wrong quietly.

---

## 10. Failure modes to recognise

| Symptom | Likely cause | Response |
|---|---|---|
| Small graph implausibly small, `status: ok` | A `filed_after` you should not have passed | Re-run with it null |
| Diversity case, clean graph, no state authority anywhere | `additional_courts` omitted | Re-run with the state high court(s) |
| Many `unscanned` rows | `max_cases` truncation | Raise the cap and re-run |
| Tier A full of irrelevant hits | Normal — expect ~1-in-6 signal | Read them; do not widen `cooccurrence_window` |
| Adverse authority count looks high | Counting rows, not decisions | Deduplicate by case name |
| Same case appears with different cluster IDs | Duplicate CourtListener records | Merge manually; the tool cannot |
| "No same-litigation history" | The fields are empty, not the record | Report as not checkable |
| `mirror_busy` | Two verifications already running | Wait; do not fall back to `show_citing_opinions` |
| Response identical after changing `additional_courts` | Possibly a true negative | Check **Courts admitted**, not the case count |

---

## 11. Cost

Single calls, measured:

| Origin | Small graph | Time |
|---|---|---|
| Iqbal | 41 | 0.7 s |
| Twombly | 31 | 0.8 s |
| Austin | 28 | 0.9 s |
| Bowers | 35 | 1.0 s |
| Roe | 220 | 2.6 s |
| Broussard | 373 | 2.8 s |
| Chevron | 396 | 5.7 s |

Cost scales with **text volume**, not case count — the graph query itself is ~5 ms and everything above is the snippet pass. That is why `max_cases` is the cost lever, not the court filter.

A full check — origin with `include_upstream`, five upstream parents, two siblings — is **8 calls and ~13 seconds**. Upstream calls carrying `filed_after` run 150–305 ms, roughly 20× cheaper than a cold check. Re-verification with `filed_after` runs ~370 ms.

Results are cached on cluster + every parameter + mirror generation + both version stamps, and checked before the mirror is touched. A repeat sweep of already-verified cases runs **7.6× faster**. Re-calling the same case with the same parameters is effectively free.

**Concurrency: 2 verifications, refused rather than queued.** Six concurrent measured at 6.5 s wall with zero refusals — the same as running them serially — because admission control serialises anyway. Concurrency buys nothing and risks `mirror_busy`. A 20-citation cite-check is ~160 calls and about **two minutes occupying both slots**; a second simultaneous cite-check will start getting refused. The mirror host is shared with every user's `opinion_view` and `fetch_opinion_file`, and saturating it trips the serving path's circuit breaker onto the CourtListener API — the quota the mirror exists to protect.

---

## 12. Recipes

**Standard first check**
```json
{"cluster_id": "<id>", "court_scope": "invalidating",
 "include_upstream": true, "include_parentheticals": true,
 "output_format": "markdown"}
```

**Federal case applying state law (Erie)**
```json
{"cluster_id": "<id>", "additional_courts": ["tex", "texcrimapp"],
 "include_upstream": true, "output_format": "markdown"}
```

**Upstream hop, per parent**
```json
{"cluster_id": "<parent>", "filed_after": "<origin's date_filed>",
 "output_format": "markdown"}
```

**Re-verifying a case checked before**
```json
{"cluster_id": "<id>", "filed_after": "<date of prior check>",
 "output_format": "markdown"}
```

**Heavily-cited origin reporting truncation**
```json
{"cluster_id": "<id>", "max_cases": 1200,
 "include_upstream": true, "output_format": "markdown"}
```

**Suspected circuit or inter-district split**
```json
{"cluster_id": "<id>", "court_scope": "invalidating_plus_peer",
 "include_upstream": true, "output_format": "markdown"}
```

**Doctrine with a specific competing test or superseding statute**
```json
{"cluster_id": "<id>", "flag_terms": ["Loper Bright", "independent judgment"],
 "include_upstream": true, "output_format": "markdown"}
```
