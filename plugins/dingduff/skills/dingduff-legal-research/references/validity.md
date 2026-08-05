# Validity and Currency

The verification discipline — confirming that every authority you rely on is *still good law*. The databases do **not** flag overturned/abrogated cases or guarantee real-time tracking of statutory amendments, so you do this yourself, every time, before any authority becomes part of an answer. This is the difference between research and a snippet dump.

Case validation comes in **two tiers**. Choosing between them is a judgment call you make per case, and you tell the user which tier each authority got.

## The two tiers

| | **Lightweight** | **Heavyweight** |
|---|---|---|
| What it is | A heuristic screen you run inline, below | The `dingduff-validity-check` skill, run in a delegated subagent |
| Cost | ~2–4 tool calls per case | A subagent and a few minutes per case; they run **one at a time** |
| The question it answers | "Does anything about this case look wrong?" | "Is this case still good law **for the proposition I am citing it for**?" |
| What a clean result means | Nothing adverse surfaced in the slice that was screened | Direct history, forward treatment, the authorities the case itself relied on, and a non-citation check all came back consistent — with the coverage limits stated |
| What a clean result does **not** mean | That the case is good law | That the case is good law *for some other proposition* |

Lightweight is a smoke test. It is fast, and it catches the loud failures — a case that has plainly been overruled, a doctrine that has plainly moved. It is not evidence of validity, because a clean screen and an unchecked case look identical.

Heavyweight is proposition-specific and states its own limits. It is the only tier whose clean result you may report as a verification.

## Choosing the tier

**The test: does the answer change if this case is bad?** If yes, heavyweight. If you find yourself reasoning that the case is *probably* fine, that is the feeling of a case that needs heavyweight.

Escalate to **heavyweight** when the case is:

- the anchor for a rule the answer asserts, or the case a memo section, brief point, or client advice rests on;
- going to be quoted or pincited in something that gets filed or sent;
- adverse authority you intend to distinguish, or authority handed to you by an opponent or a client;
- old enough, prominent enough, or contested enough that its status is genuinely in question;
- flagged by anything at all in the lightweight screen. **Do not adjudicate a treatment signal with the screen** — the screen reads snippets, and a snippet saying "we decline to follow *Smith*" may be quoting a party or a court that was itself reversed. Escalate instead.

**Lightweight is enough** when the case is:

- background, descriptive, or one of several redundant supports for a point nobody disputes;
- part of a quick orientation pass with no filing or advice behind it — the user asked what the law is, not for something to rely on;
- being screened as part of a large network, to decide which few cases earn heavyweight.

Weigh the cost honestly. Heavyweight checks are sequential and slow; running one on all forty cases in a network is not thoroughness, it is a way to spend an hour confirming that thirty-eight background cites are fine. Screen broadly, escalate narrowly, and put the expensive check where the argument actually bears weight. When the count of load-bearing cases is high, say so and ask the user which ones matter rather than silently picking.

Statutes and regulations have no tier split — the currency checks below apply to all of them.

## Lightweight validation — the screen

For each case:

1. Run `show_citing_opinions` against it, ordered by `-dateFiled`, and read the snippets of recent citing cases:
   ```json
   {"identifier": "<reporter cite or cluster_id>", "order_by": "-dateFiled", "limit_results": 20}
   ```
2. Scan for **treatment signals**: "abrogated," "overruled," "is no longer good law," "rejected," "declined to follow," "limited to its facts," "called into doubt," "superseded by statute." Any of these is a red flag — and a trigger to escalate, not something to resolve here.
3. Cross-check with a direct search: `opinion_search` for `"<case name>" AND (overruled OR abrogated OR "no longer good law")`.
4. Confirm a **recent application** exists for the proposition (within ~5 years, or the most recent available if the doctrine is dormant) — this shows the rule is alive, and surfaces recent narrowing.
5. For foundational SCOTUS or controlling appellate cases, screen at least the ~20 most recent citing cases.

A screen that returns nothing is **not** a finding of validity. Record it as screened, not as verified.

If the screen turns up adverse treatment and heavyweight is unavailable to you, retrieve the treating case via `fetch_opinion_file`, read it, and determine the **scope** — full overruling, partial abrogation, narrowing, or mere distinguishing. Never characterize treatment from a snippet.

If a case has been overruled or substantially abrogated, **do not present it as good law** — note the treatment, explain the current rule, and cite the case that did the overruling. A non-controlling or overruled case presented as authority is the worst failure mode in legal research.

## Heavyweight validation — delegate it

Hand the case to `dingduff-validity-check` **in a subagent** (use Opus). Do not load that skill into your own context — the check reads full opinions and will flood the research thread.

Give the subagent all four:

1. **The case** — full citation, plus the cluster ID if you have it.
2. **The proposition** — the specific rule you are citing it for. Required; validity is proposition-specific and the check cannot run without it.
3. **Jurisdiction and posture** — the target court, and whether the case is being applied in diversity.
4. **The role** — anchor, supporting cite, or adverse case being distinguished.

You get back a short structured verdict — one of VALID / VALID BUT NARROWED / AT RISK / QUESTIONED / INVALID FOR THIS PROPOSITION / INVALID / INDETERMINATE — with a confidence level, the replacement authority if the case is unusable, and an explicit coverage statement. Carry that verdict and its confidence into your output rather than restating it in your own words.

Run these **sequentially**. Do not launch several validity subagents at once; they contend for the same capacity and will slow each other down.

If the subagent reports that the check ran without its underlying tool, its confidence caps at moderate — pass that limitation through to the user rather than absorbing it.

## Currency and amendments (statutes and regulations)

Code databases store statutory and regulatory text as imported and may lag amendments or repeals:

- When `codes_view` returns a section, note any effective-date / version annotation it carries (or retrieve section metadata via `metadata_view`).
- Where the statutory text drives the answer, run a recency check: `opinion_search` for recent cases citing the section — if a case discusses an amended version different from the text you have, flag it.
- For federal statutes especially, surface the text you found and flag possible amendments for the user to confirm against an authoritative `.gov` source.
- Watch for **"superseded by statute"** treatment of cases that construed a prior version of the text — the old gloss may no longer apply.
- **Regulations** (agency/administrative codes, the C.F.R.) are amended and repealed too — check their effective dates and any superseding amendments the same way, and confirm the agency hasn't revised the rule since the database's import.

Never silently rely on a stale version of a statute.

## The verification pass (before drafting any answer)

Run through every authority you plan to cite in a primary/anchor/controlling role:

- [ ] Every case screened with lightweight validation.
- [ ] A tier assigned to each case, for a reason you could defend — and every load-bearing case escalated to heavyweight.
- [ ] Every heavyweight verdict recorded with its confidence and its coverage limits.
- [ ] Any adverse-treatment signal escalated to heavyweight, or — if unavailable — the treating case retrieved, read, and its scope determined.
- [ ] A recent application located for each main proposition (or dormancy noted).
- [ ] No more-recent controlling case from the same court (or higher) supersedes a case you rely on.
- [ ] Statutory sections checked for effective-date/amendment annotations; stale text flagged.
- [ ] Interpreting cases (from statutory research) put through the same tiering.

## Tell the user what got which

The user cannot see which cases you screened and which you verified, and in a finished answer the two look identical. Say it explicitly — in the **Validity confirmations** section, and in the `Validity` column of the case table.

Use these labels:

- **Verified (heavyweight)** — plus the verdict, the confidence, and the proposition it was checked for: *"Verified (heavyweight) — VALID for the presumptive-enforceability holding, high confidence."*
- **Screened (lightweight)** — plus what was screened: *"Screened (lightweight) — no adverse signals in the 20 most recent citing opinions."*
- **Not validated** — for anything that got neither. Say so rather than leaving it blank.

Then add one line naming the tradeoff you made: which cases you escalated and why, and which you left at a screen. If **nothing** received heavyweight validation, say that in as many words — an answer that never mentions the tiers reads as though everything was verified.

Never present a lightweight screen as a verification, and never let a heavyweight verdict lose its stated limits on the way into your output.
