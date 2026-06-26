---
name: dingduff-legal-analysis
description: Analyze a legal question rigorously and produce a citation-anchored analysis or proof skeleton — frame the issues, synthesize the governing rule, analyze the facts, organize the proof (CRAC/CREAC), and deploy authority. Use for ANY legal-reasoning task — "what's the law on X," "do we have a claim," "will this hold up," "analyze whether," "what are the issues," "how would we argue this" — and to build the analytical skeleton before drafting any memo, brief, or letter. Pairs with dingduff-legal-writing (which turns the analysis into a finished document) and the dingduff research and citation skills. Detailed method for each step lives in references/ and is loaded as needed. (v1.2)
---

# Legal Analysis

This skill is the reasoning engine: it turns a legal question, facts, and retrieved authority into a sound, inspectable **analysis** — and, when a document will follow, the **proof skeleton** that `dingduff-legal-writing` drafts from. It covers issue framing, rule synthesis, fact analysis, proof structure, and the use of authority. Keep this file in context as the spine; pull in a `references/` file for the step you're on.

## CRITICAL discipline (the whole skill rests on this)

- **Retrieved authority only.** Never state a rule, holding, quote, or citation from memory or a search snippet. Retrieve the source first (via `dingduff-legal-research`, or sources the user supplied), then state it. Every rule and authority in the analysis must trace to a real, retrieved source.
- **Skeleton before prose.** Produce the analytical skeleton — conclusion, rule, proof, application, each tagged with a real citation — before writing any polished prose. Fluent prose is where wrong analysis hides; the skeleton forces the reasoning into the open.
- **Calibrate depth to the stakes.** Most questions need one disciplined pass. For high-stakes matters — appellate briefs, dispositive motions, formal opinions, novel/first-impression issues — go exhaustive: each reference has a **"Going further"** section describing the deeper work (full issue inventories, every rule formulation, alternative proof structures, complete authority neutralization).
- **Escalate, don't paper over.** If a step exposes a gap — missing authority, an unsettled rule, an unsupported fact — stop and go back (to research, or to the earlier step) rather than writing confident prose over the hole.
- **Predictive vs. persuasive.** Predictive analysis (for a memo or client advice letter, "will we win") is objective and weighs both sides. Persuasive analysis (for a brief, motion, or demand letter) orders and frames for advantage but never misstates the law or facts.

## The workflow

Run these in order; each consumes the previous step's output. Load the cited reference for method detail.

1. **Frame the issues** — work from the user's question and the **facts/record they provide**; gather or confirm the factual record first, and if determinative facts are missing, ask the user. Then spot, select, narrow, and order the issues; fix the theory of the case and the controlling perspective. → `references/issue-framing.md`
2. **Get the authority** — if the governing law isn't in hand, use `dingduff-legal-research` until it is, validity-checked. Return here whenever a later step surfaces a new question — research and analysis interleave.
3. **Synthesize the rule** — state the governing rule and structure it (elements / factors / standard); reconcile conflicts. → `references/rule-synthesis.md`
4. **Analyze the facts** — identify the legally significant facts, classify them, map them to the rule's elements. → `references/fact-analysis.md`
5. **Structure the proof** — organize each conclusion's proof conclusion-first (CRAC/CREAC), separate rule proof from application, calibrate depth, nest multiple conclusions. → `references/proof-structure.md`
6. **Deploy authority** — analogize/distinguish cases and build statutory-interpretation arguments as you build the proof. → `references/applying-authority.md`

Output: a labeled proof skeleton (ordered, nested, citation-anchored). When a document will follow — predictive or persuasive — the skeleton is the required hand-off to `dingduff-legal-writing`. Write the analysis up as the finished deliverable only when the analysis itself is what the user wants (no document to follow).

## The proof unit (the spine, in brief)

Every legal conclusion is proved with one unit, in this order — **C**onclusion (stated first) → **R**ule → **E**xplanation/rule proof → **A**pplication to the facts → **C**onnection-conclusion. Never intermingle rule proof and application: finish proving what the rule *is* before applying it. Simple, uncontested points get a compressed unit; contested, dispositive points get a full one. Full method, depth calibration, and worked examples in `references/proof-structure.md`.

## References map

Load the one you need:

- `references/issue-framing.md` — spotting, selecting, narrowing, framing, and ordering issues; the four-question classification (fact / definition / evaluation / procedure); theory of the case; idea-generation techniques; going further (exhaustive inventory, competing framings, preservation, cross-issue interaction).
- `references/rule-synthesis.md` — the four kinds of rules; structuring a rule (elements / factors / standard); inductive synthesis across authorities; reconciling conflicts; weight-of-authority hierarchy; going further (every formulation, definitional architecture, mapped splits, trajectory).
- `references/fact-analysis.md` — identifying legally significant facts; classifying by significance, valence, and status; characterizing accurately; mapping facts to rule elements; fact-vs-conclusion discipline.
- `references/proof-structure.md` — the CRAC/CREAC proof unit; conclusion-first ordering; depth calibration (conclusory / substantiating / comprehensive; Ignore / Tell / CRAC / CREAC); nesting and umbrellas; predictive vs. persuasive ordering; worked example; going further (alternatives, fallbacks, counter-structures, coherence audit).
- `references/applying-authority.md` — using precedent (analogize/distinguish, holding vs. dicta, parentheticals, quotation); statutory argument (text, canons, intrinsic/extrinsic); handling adverse authority; the canons table; going further (every analogy and canon, full neutralization).

## Related skills

Input: `dingduff-legal-research` (gathers and validity-checks the authority, flagging statutory currency for confirmation; interleaves with this skill so analysis guides research and research guides analysis). Next step: `dingduff-legal-writing` (drafts a document from the skeleton). QC: `dingduff-legal-citation-format`, `dingduff-citation-check`.
