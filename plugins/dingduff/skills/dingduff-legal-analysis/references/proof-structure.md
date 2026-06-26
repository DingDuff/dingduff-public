# Proof Structure

Method for organizing the proof of a legal conclusion into an inspectable skeleton **before any prose**. This is the reasoning spine. Output: a labeled, ordered, nested set of proof units, each with depth tags and real citations.

## The proof unit (CRAC / CREAC)

Every conclusion is proved with one unit, parts in this order:

- **C — Conclusion / Assertion**, stated *first*. (Predictive: the predicted answer. Persuasive: the position, as an assertion.) The reader needs to know where the proof is going before it starts.
- **R — Rule** that governs (from `rule-synthesis.md`), stated as the rule — not as a discussion of cases.
- **E — Rule proof / Explanation** — proof that the rule *is* what you say: the authority, synthesis, policy that establishes it.
- **A — Application** — apply the *proven* rule to the determinative facts (from `fact-analysis.md`); analogize/distinguish (see `applying-authority.md`).
- **C — Connection-conclusion** — restate and connect to the larger point.

**Cardinal rule: never intermingle rule proof and application.** Finish proving what the rule *is* before applying it; a reader rightly resists applying a rule whose proof isn't complete.

## Steps

1. **Inventory the conclusions to prove** — usually one per contested element/factor/sub-issue, plus the umbrella conclusion they add up to. Name every element even if you'll mark it undisputed; note any threshold/dispositive issue (it leads).
2. **Build a unit for each** — fill the five parts as terse bullets (not prose), tagging every Rule/Proof/Application line with the real citation + pincite.
3. **Calibrate depth** (below).
4. **Order and nest** (below).
5. **Self-check and escalate** — every conclusion present; conclusion-first; proof and application not intermingled; every rule/authority traces to a retrieved source; depth calibrated; ordering/framing matches posture. If a unit exposes a gap, stop and route back rather than writing over it.

## Depth calibration

> Give explanation in depth **exactly proportional to the reader's skepticism** — enough to allay doubt, never more than will be read.

Depth is a budget; spend it on the few outcome-determinative points and compress the rest. Equal coverage of every element is almost always mis-calibrated. Two compatible scales:

**Depth of a part** (set separately for rule proof and application):

| Depth | Looks like | Use when |
|---|---|---|
| **Conclusory** | State it; little/no support. | Obvious or undisputed. |
| **Substantiating** | State, cite, briefly support. | The default. |
| **Comprehensive** | Full development; multiple authorities; counterarguments answered. | Contested *and* could decide the matter. |

**Whole-unit compression** (quick triage, esp. persuasive):

| Move | Contents | Use when |
|---|---|---|
| **Ignore** | (omit) | Genuinely irrelevant. |
| **Tell** | Conclusion only. | Element present and undisputed. |
| **CRAC** | Conclusion + Rule + Application (minimal proof). | Rule settled; the fight is the facts. |
| **CREAC** | Full unit, developed. | Rule *and* application contested. |

To choose fast: Is it disputed? (no → Tell.) Is the dispute about the rule, the facts, or both? (rule → develop proof; facts → CRAC; both → CREAC.) Could it alone decide the outcome? (yes → comprehensive regardless.) What will *this* reader doubt?

## Ordering and nesting

- **Nest** multi-part proofs: each element/sub-issue is its own unit, gathered under an **umbrella unit** that states the overall conclusion up front and resolves it at the end. Keep nesting shallow.
- **Order** by posture: **predictive** — conclusion first, then elements in logical order, weaknesses handled candidly. **Persuasive** — strongest/dispositive first, affirmative before defensive; frame the rule favorably within what the authority honestly supports.
- **Vary the C-R-E-A-C sequence** within a unit only for a real, articulable reason (usually persuasive strategy) and only if the gain beats the clarity cost.

## Worked example (illustrative; placeholder cites)

Claim: promissory estoppel (promise; reasonable expectation of reliance; actual reliance; injustice avoidable only by enforcement). Elements 1–3 clearly met; the case turns on element 4. Well-calibrated predictive skeleton:

```
[UMBRELLA] Conclusion: a court will likely find promissory estoppel.
  Rule: PE requires (1) promise, (2) reasonable expectation of reliance,
        (3) actual reliance, (4) injustice avoidable only by enforcement. — §90 [illus.]; cite
  El. 1 Promise ............ TELL — the Sept. 3 email pledged $50k. (conclusory)
  El. 2 Expectation ........ TELL — email said "go ahead and order." (conclusory)
  El. 3 Actual reliance .... CRAC — plaintiff ordered $48k three days later. — record cite
  El. 4 Injustice (DISPOSITIVE) ... CREAC — COMPREHENSIVE
     Rule: courts weigh definiteness, reasonableness/extent of reliance, other remedies. — cite
     Proof: synthesize the line drawing the limit; policy (protect reliance vs. windfalls). — cites
     Application: apply each factor; analogize [Case A], distinguish [Case B]; answer the
        mitigation counterargument. — cites
     → Injustice avoidable only by enforcement; estoppel lies.
```

Three elements collapse to a line each; the dispositive element gets the whole budget. That allocation is the skill.

## Going further (high-stakes matters)

- **Exhaustive conclusion inventory** — primary conclusion, independent **alternative** grounds (argue in the alternative), **fallbacks** (if not X then Y), and the conclusions the **opponent** must establish (build a unit answering each).
- **Map counter-structures** — for central conclusions, lay out the plausible alternative proof structures (rule-based vs. analogical; different rule formulations) and choose the one that is strongest *and* hardest to attack; pre-build the opponent's structure so each of their units meets a prepared answer.
- **Push the contested core to comprehensive**; compress everything else hard.
- **Whole-structure coherence audit** — read the entire skeleton as one thing: no unit contradicts another, alternatives are genuinely independent, no concession sinks another unit, the order honors every required sequence.
