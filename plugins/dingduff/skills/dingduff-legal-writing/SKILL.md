---
name: dingduff-legal-writing
description: Draft and revise legal documents — office memos, trial-court motion briefs, appellate briefs, demand letters, and client advice letters — and run the writing craft passes (organize, persuade, edit for clarity). Use for ANY legal drafting or revision task — "write/draft a memo," "draft a motion or brief," "respond to their motion," "write a demand/client letter," "make this more persuasive," "organize/tighten/clean up this draft," "write the question presented / statement of facts / point headings." It first builds the analysis (via dingduff-legal-analysis), then drafts from the proof skeleton using the right document anatomy, then runs craft passes and cite-checking. Document anatomies, components, and craft detail live in references/ and are loaded as needed. Pairs with dingduff-legal-analysis and the dingduff research and citation skills. (v1.2)
---

# Legal Writing

This skill turns legal analysis into finished work product — memos, briefs, motions, and letters — and provides the craft passes (organization, persuasion, clarity) that any legal document needs. It is the drafting layer; the reasoning it drafts from comes from `dingduff-legal-analysis`. Keep this file in context as the orchestrator; pull in a `references/` file for the document or pass you're on.

## CRITICAL discipline

- **Analyze before you draft (skeleton before prose).** Do not write document prose until the analytical skeleton exists — conclusion, rule, proof, application, each anchored to a *retrieved* source. Build it with `dingduff-legal-analysis` first. Fluent prose is where wrong analysis hides.
- **Predictive vs. persuasive.** A memo or client letter *predicts* — objective, both sides shown, honest confidence. A brief, motion, or demand letter *argues* — persuasive, but never misstating law or facts, and disclosing adverse controlling authority. Don't slant a memo; don't write a brief that reads like a neutral memo.
- **Calibrate depth to the stakes.** Most documents need one disciplined pass; for high-stakes work (appellate briefs, dispositive motions, opinion-grade memos) go exhaustive, as each reference's **"Going further"** section describes.
- **Defer to local rules.** Court and firm rules on format, length, required sections, and certificates always win over the defaults in the references.
- **Escalate, don't paper over.** If drafting exposes a gap — missing authority, an unsynthesized rule, an unsupported fact — stop and return to `dingduff-legal-analysis` or `dingduff-legal-research` rather than writing around it.

## The workflow

1. **Analyze first** — run `dingduff-legal-analysis` to produce the citation-anchored proof skeleton (frame issues → research → synthesize rule → analyze facts → structure proof → apply authority). This is itself the recursive research↔analysis loop, not a one-time pass — it is complete only when the authority is saturated and the analysis is gap-free. Everything below drafts *from* that skeleton.
2. **Pick the document type** and load its reference (router below).
3. **Draft the parts** from the skeleton, using the document's anatomy and the component references (question presented, statement of facts, point headings, standard of review).
4. **Organize** — roadmap, headings, topic sentences, transitions. → `references/organization.md`
5. **Persuade** (advocacy documents only — skip for memos) — theme, story, framing, emphasis, equity/policy, on a foundation of candor. → `references/persuasion.md`
6. **Edit for clarity** — sentence, word, and paragraph level, without changing substance. → `references/clarity.md`
7. **Cite-check and format** — `dingduff-legal-citation-format` (large — delegate it to a subagent), then `dingduff-citation-check` (runs an interactive attorney review of the cites).

## Document router

| Want | Posture | Reference |
|---|---|---|
| Office / interoffice memo | predictive | `references/memo.md` |
| Trial-court motion or opposition | persuasive | `references/motion-brief.md` |
| Appellate brief (opening / answer / reply) | persuasive | `references/appellate-brief.md` |
| Demand letter to an opposing party | persuasive | `references/letters.md` |
| Client advice letter | predictive | `references/letters.md` |
| One section only (QP, facts, headings, standard) | — | `references/components.md` |
| Organize / make persuasive / tighten an existing draft | — | `references/organization.md` · `references/persuasion.md` · `references/clarity.md` |

## References map

- `references/memo.md` — the predictive office memo: anatomy (Question Presented, Brief Answer, Statement of Facts, Discussion, Conclusion), predictive discipline, template, and opinion-grade "going further."
- `references/motion-brief.md` — the persuasive trial-court brief/opposition: anatomy (introduction, facts, legal standard, argument, relief), posture (movant vs. opponent), and dispositive-motion "going further."
- `references/appellate-brief.md` — the appellate brief: full anatomy (issues, statement of the case, standard of review, summary of argument, argument, conclusion), the appellate disciplines (standard of review per issue, preservation, record-only facts), and high-court "going further."
- `references/letters.md` — the demand letter (persuasive, to an adverse party; ethics and client-protection) and the client advice letter (predictive, plain-language, recommendation + caveats).
- `references/components.md` — the reusable parts: question presented (+ brief answer), statement of facts, point headings, standard of review — predictive and persuasive forms, with examples.
- `references/organization.md` — large-scale organization: roadmaps and umbrellas, headings, topic sentences, transitions, and reverse-outlining to diagnose a draft.
- `references/clarity.md` — the clarity edit: the sentence-fault checklist, word/usage fixes, paragraph flow, and the four fundamentals — without changing legal substance.
- `references/persuasion.md` — the advocacy layer: the three appeals, theme, legal storytelling, framing, positions of emphasis, identification, equity/policy, and the ethos/candor guardrails.

## Related skills

Upstream: `dingduff-legal-analysis` (builds the skeleton this skill drafts from) and `dingduff-legal-research` (gathers and validity-checks the authority). QC: `dingduff-legal-citation-format`, `dingduff-citation-check`.
