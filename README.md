# DingDuff

### A free legal‑research connector for Claude — built by lawyers, for lawyers.

DingDuff links your own Claude account to a database of **millions of court
opinions**, **federal and state statutes and rules**, and **federal court
filings (PACER)** — so you can do real legal research, with real citations,
right inside Claude. No new app to learn, no Boolean gymnastics: you ask Claude a
legal question in plain English, and it searches the actual sources and answers
with authority you can click through and verify.

> *"DingDuff is a must‑have for every litigator. Instead of spending hours
> devising Westlaw search terms, I can now get legal research through plain
> English prompts, just like working with an associate."*
> — **Michael Showalter**, Litigator

**[Sign up at dingduff.com »](https://dingduff.com)**  ·  [Installation guide (wiki)](https://github.com/DingDuff/dingduff-public/wiki)  ·  [Watch the 2‑minute demo](https://youtu.be/1ts9kdMKjJg)  ·  [Skills library ↓](#the-skills-library)

> **This repository** is DingDuff's public home: the [installation & help
> wiki](https://github.com/DingDuff/dingduff-public/wiki) and downloadable copies
> of the optional [skills](#the-skills-library). To *use* DingDuff you connect it
> to Claude — start with the wiki.

---

## Contents

- [What DingDuff is](#what-dingduff-is)
- [What you can do with it](#what-you-can-do-with-it)
- [What's covered](#whats-covered)
- [The tools](#the-tools)
- [How it works](#how-it-works)
- [The skills library](#the-skills-library)
- [Getting started](#getting-started)
- [Citation checking: reliable and private](#citation-checking-reliable-and-private)
- [Who it's for](#who-its-for)
- [What lawyers are saying](#what-lawyers-are-saying)
- [Pricing](#pricing)
- [Who's behind it](#whos-behind-it)

---

## What DingDuff is

DingDuff is a **connector** (an MCP connector, in Claude's terms) that plugs a
comprehensive legal database into the Claude you already use. Once it's added,
Claude can search and read primary law directly — the same way a research
associate would — and hand you answers grounded in citations rather than in its
own memory.

We built DingDuff for our own daily practice, and the design philosophy shows: it
**gets out of the AI's way.** We didn't wrap Claude in guardrails or try to teach
it how to lawyer. We just gave it clean, direct access to the sources and let it
work. In our hands that has consistently outperformed the purpose‑built legal‑AI
products we used to pay for — enough that we quietly stopped using them.

The trade‑off is deliberate: because DingDuff is hands‑off, **the lawyer reading
the output is the guardrail.** That's why it's built for attorneys, and why every
answer is something you can open, read, and verify yourself.

## What you can do with it

Ask in plain English; Claude does the digging. For example:

- *"Find recent Ninth Circuit cases on the economic‑loss rule and give me
  citations."*
- *"Pull the full text of* Twombly *and summarize the pleading standard it sets."*
- *"What does Texas Civil Practice & Remedies Code § 16.003 say, and what's the
  discovery rule around it?"*
- *"Show me every published opinion that has cited* this case *— is it still good
  law?"*
- *"Find the docket for* this federal case *and get me the motion to dismiss."*
- *"Research this question, then draft me an office memo — and cite‑check it when
  you're done."*

The result is a research memo, a doctrinal map, a stack of saved opinions on your
desktop, or a verified draft — whatever you asked for, with citations you can
trust.

## What's covered

DingDuff draws on a database compiled largely from
[CourtListener](https://www.courtlistener.com) (whose data heroes made this whole
project possible) plus federal and state statutory sources:

| Federal | Every state — all 50 + D.C. |
|---|---|
| Federal court opinions (trial, appellate, Supreme Court) | State court opinions |
| Federal statutes & regulations (U.S.C. / C.F.R.) | State statutes & codes |
| Federal Rules of Civil Procedure | State Rules of Civil Procedure |
| Federal Rules of Appellate Procedure | State Rules of Appellate Procedure |
| Federal Rules of Evidence | State Rules of Criminal Procedure |
| Federal court filings via **PACER** | State Rules of Evidence |

## The tools

Under the hood, DingDuff gives Claude a focused set of research tools. You never
call these directly — Claude picks the right ones for your question — but here's
what it can reach for:

### 📚 Case law
- **Search court opinions** across federal and state courts, in plain English or
  with Boolean operators, filtered by jurisdiction, court, date, judge, or
  precedential status.
- **Read the full text** of any opinion, or get just the **case metadata** —
  court, date, precedential status, reporter citations, judges, and how many
  times the case has been cited.
- **Trace the citation network:** a built‑in citator finds every opinion that
  **cites** a given case, and surfaces **related** opinions on the same issue —
  so you can check whether authority is still good law and follow a doctrine
  forward and backward.
- **Save your own copy** of any opinion (full text) to a folder on your computer,
  so your research library is yours to keep.

### 📜 Statutes, codes & rules
- **Search** federal and state statutes, regulations, and court rules.
- **Browse a code's structure** the way you'd page through the book — title →
  chapter → section.
- **Pull the exact text** of a section, and **save your own copy** alongside your
  cases.

### 🏛️ Federal court filings (PACER)
- **Find dockets** by case or by **party / attorney**.
- **View a docket sheet**, open **individual filings**, and **search within a
  docket** — or **across many dockets** — for the document you need.
- **Check availability** before you pull anything, and **follow related docket
  entries**.

### ✓ Citation checking
- After you draft, **verify every citation** in the document against the actual
  source text and open an **interactive review panel** where you — the attorney —
  give the final verdict on each cite. (See
  [below](#citation-checking-reliable-and-private).)

## How it works

From your side, it's three steps — and none of them are technical.

**1. Connect it once.** In your Claude account you add DingDuff as a custom
connector (paste one URL, sign in with your DingDuff login). The
[wiki](https://github.com/DingDuff/dingduff-public/wiki) walks you through it —
or you can paste the wiki link into Claude and have Claude walk *you* through it,
one step at a time.

**2. Ask Claude, in plain English.** Once connected, you just ask legal questions
the way you'd ask a colleague. Claude searches DingDuff, reads the real opinions
and statutes, and answers with citations. (Tip: tell Claude to *use only DingDuff
and always give citations* — you can set that once as a standing instruction so
you don't repeat it.)

**3. It adapts to where you run Claude:**

- **Claude Cowork (desktop app) — recommended.** Claude can reach a folder on
  your computer, so instead of dumping opinions into the chat it **saves your own
  full copy of each case and statute to a desktop folder** you can revisit later.
  This is DingDuff at its best.
- **The Claude web app or your phone.** DingDuff runs here too — just switch on
  Claude's code‑execution and network settings (a one‑time toggle; the wiki shows
  you where) so it can save sources. On mobile, searching and reading work great;
  saving files and cite‑checking need the desktop app or a browser.
- **Add the optional [skills](#the-skills-library).** Free, one‑time downloads
  that make Claude's legal answers noticeably sharper and more consistent.

We've never seen DingDuff hallucinate a fake case or statute — but Claude will
occasionally get something wrong, which is exactly why a lawyer reads and checks
the work.

## The skills library

DingDuff works well on its own. These **free skills** make it noticeably better —
they teach Claude the craft of legal research, analysis, and
cite‑checking. Each is a one‑time download that you upload to Claude once; it then
lives in your skill picker and triggers automatically when relevant.

| Skill | Version | What it does |
|-------|:---:|--------------|
| **Legal Research** — [`download`](dist/dingduff_legal-research_v2.1.skill) | v2.1 | End‑to‑end research: finds, retrieves, reads, and **validates** the controlling cases, statutes, and regulations; maps the citation network and statutory landscape; confirms everything is still good law. Scales from a quick "what's the law on X" to a full doctrinal map. |
| **Legal Analysis** — [`download`](dist/dingduff_legal-analysis_v1.2.skill) | v1.2 | The reasoning engine: frames the issues, synthesizes the governing rule, analyzes the facts against it, organizes the proof (CRAC/CREAC), and deploys authority. Use before drafting anything. |
| **Citation Check** — [`download`](dist/dingduff_citation-check_v2.4.5.skill) | v2.4.5 | After you draft a memo (Markdown, Word, or Google Docs), verifies every citation against your stored sources plus anything else you supply, quality-checks each highlighted passage for substance, then opens an interactive attorney review panel and records your verdicts. |
| **Legal Citation Format** — [`download`](dist/dingduff_legal-citation-format_v1.4.skill) | v1.4 | Formats citations the way courts expect — signals, pincites, short forms (*id.*/*supra*), string cites, block quotes. Follows *The Indigo Book*. Form only; works standalone (no connector needed). |

The research and analysis skills are designed to work **together**: research
gathers the authority, and analysis reasons through the question to build the
proof. Citation Check then verifies your finished work product; Legal Citation
Format polishes the cites.

**Install a skill:** download the `.skill` file above (on GitHub, open the file
and use **Download raw file**), then upload it to Claude —

- **Cowork (desktop):** **Customize** (upper‑right) → **Skills** → upload the file.
- **claude.ai (browser):** **Settings → Capabilities → Skills** → upload the file.
- **Claude Code (CLI):** install the whole library at once as a plugin:
  ```
  /plugin marketplace add DingDuff/dingduff-public
  /plugin install dingduff@dingduff
  ```

Skill files are named `dingduff_<skill>_vX.Y.skill`; in Claude's picker they
appear under their `dingduff-…` name. To update, re‑download and re‑upload (or
`/plugin marketplace update dingduff`). Citation Check needs `python3`, which
Cowork and Claude Code provide.

## Getting started

You need two things:

1. **Your own Claude plan.** A paid plan (Pro, Max, Team, or Enterprise) is
   recommended; the **desktop app with Cowork** is the best experience. (The Free
   plan works but allows only one custom connector.)
2. **A DingDuff login.** Sign up at **[dingduff.com](https://dingduff.com)** —
   this is the email and password you'll use to connect. DingDuff is for licensed
   attorneys, per the [Terms of Service](https://dingduff.com/terms).

Then follow the **[installation wiki](https://github.com/DingDuff/dingduff-public/wiki)**.
The short version: add a custom connector in Claude pointing at

```
https://app.dingduff.com/mcp
```

sign in, allow the tools, and confirm it works by asking Claude *"Does the
DingDuff connector have the `opinion_search` tool?"* The wiki also covers browser
setup, Team/Enterprise plans, mobile, and troubleshooting.

## Citation checking: reliable and private

DingDuff's citation checker takes a piece of legal writing you've drafted, checks
**every citation against the actual source text**, and opens a review panel where
**you give the final word** on each one — then produces a printable audit record
for the file.

- **Quotes are verified by code, not by the AI's memory.** Claude proposes the
  supporting passage; a small program running in *your own session* then searches
  the real source file for that exact text. A made‑up or misremembered quote
  can't slip through as a verified highlight. (The matching forgives cosmetic
  differences — spacing, curly quotes, hyphenation across line breaks.)
- **You see the evidence, and you give the verdict.** For each citation you get
  the claim, the highlighted passage in the source, and your document side by
  side, and you mark it **verified**, **needs attention**, or **rejected** — with
  a note where useful.
- **It's private by design.** The checking runs entirely on your machine and
  sends nothing. The interactive panel passes your document through DingDuff only
  as the arguments needed to draw it, never stored or logged — and there's a
  standalone `review.html` if you'd rather nothing transit at all. DingDuff keeps
  no copy of your draft or your verdicts.

It checks against authorities you saved from DingDuff **and any source you supply
yourself** — a Restatement section, a case that isn't in CourtListener, the other
side's brief, a factual exhibit. Full explainer:
[How Citation Checking Works](https://github.com/DingDuff/dingduff-public/wiki/Citation-Checking).

## Who it's for

DingDuff is for **lawyers.** Its hands‑off design is the source of both its power
and its one caveat: without heavy guardrails, Claude + DingDuff is remarkably
capable, but it can occasionally get something wrong. With DingDuff, the attorney
reading and checking the output *is* the guardrail — which is why a lawyer‑user is
essential, and why we make DingDuff available only to licensed attorneys (you
confirm this when you accept the [Terms of Service](https://dingduff.com/terms)).

## What lawyers are saying

> *"DingDuff is a game changer and I honestly can't imagine practicing without
> it. It has completely changed legal research for me from a slog to something I
> can complete in minutes. Even after spending hours doing research I was always
> worried I was missing something. And Westlaw's AI, while helpful, is still
> regularly incomplete or inaccurate. DingDuff is giving me confidence in my
> ability to do legal research quickly and thoroughly, and I use it daily in my
> practice. I also regularly get partner feedback that they are blown away by the
> research memos I put together using DingDuff and Claude. I can't imagine going
> back to a world without it."*
> — **Laura Bach**, Litigator

> *"DingDuff is a must‑have for every litigator. Instead of spending hours
> devising Westlaw search terms, I can now get legal research through plain
> English prompts, just like working with an associate. I recently filed a
> thoroughly researched Ninth Circuit opening brief with DingDuff — without once
> opening Westlaw. It simply wasn't needed."*
> — **Michael Showalter**, Litigator

## Pricing

**DingDuff is free while in beta.** Our running costs are low enough that we
support the project with a **tip jar** rather than subscriptions — if it saves you
time and you'd like to help keep it free, there's a tip option at
[dingduff.com](https://dingduff.com/#cost). No subscription, no per‑search
billing.

## Who's behind it

DingDuff started as a side project by two practicing lawyers — **Kyle Dingman**
and **Stephanie Duff‑O'Bryan** — who wanted a research tool they could use in
their own day jobs. It began as a scrappy interface to a database running on a
Raspberry Pi in a closet; over a couple of years of iterating, it grew into
something that (to our surprise) kept outperforming our firms' Westlaw‑AI
accounts. We brought on developers **Julia Teleki** and **Jeremy** to turn a
personal project into something we could share, and now we're making it available
to other lawyers.

This project would not be possible without the data heroes at
**[CourtListener](https://www.courtlistener.com)** / Free Law Project.

---

**Links:** [dingduff.com](https://dingduff.com) · [Installation & help wiki](https://github.com/DingDuff/dingduff-public/wiki) · [Demo video](https://youtu.be/1ts9kdMKjJg) · [Terms of Service](https://dingduff.com/terms) · Questions? [hello@dingduff.com](mailto:hello@dingduff.com)

*Skills in this repository are developed in the DingDuff MCP server and vendored
here for distribution; each `dist/dingduff_<skill>_vX.Y.skill` is a packaged copy
of the matching `plugins/dingduff/skills/dingduff-<skill>/` folder.*
