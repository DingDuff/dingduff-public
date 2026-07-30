<!--
INSTRUCTIONS FOR CLAUDE
These are optional but recommended add-ons. Help the user install the skills they
want and apply the recommended settings. Skill install location differs by
environment (Cowork desktop vs claude.ai vs Claude Code). The citation-check
skill needs python3 and stored source files. Keep it simple; the research skills
trigger on their own once installed.
-->

# Skills & Recommended Settings

DingDuff works on its own, but these skills make it noticeably better. None are
strictly required — though **`dingduff-legal-research`** is one we'd strongly
recommend; see below.

**The easiest way to get them is our plugin**, which installs all our skills at
once and keeps them current. Skip the file-by-file downloads unless you want to
pick and choose.

## Install the plugin (recommended)

1. In Claude, open **Customize** → the **Plugins** tab.
2. Under **Personal plugins**, click **+** → **Add marketplace** →
   **Add from a repository**.
3. Enter `DingDuff/dingduff-public`.
4. Click **Install** on the **DingDuff** plugin.

Plugins work in **Cowork**, the **desktop app**, and **claude.ai in a browser**.
When we ship a new version of a skill it arrives through the marketplace, so you
don't have to come back and re-download each file yourself.

In **Claude Code**, do the same thing from the CLI:

```
/plugin marketplace add DingDuff/dingduff-public
/plugin install dingduff@dingduff
```

The `/plugin` menu there also has an **auto-update** toggle for the DingDuff
marketplace.

> Prefer to install skills one at a time? Each skill below has a direct download,
> and ["Install a single skill by hand"](#install-a-single-skill-by-hand) covers
> where to upload it.

## The skills

### Legal research

- **`dingduff-legal-research`** (v2.4) — **strongly recommended.** DingDuff works
  without it, but it works a lot better with it: this skill carries the research
  method and the bulk of our anti-hallucination instructions, which can't be
  delivered through the connector itself. If you install only one, install this
  one. It's one skill for legal research generally: it finds, retrieves, reads, and **validates** the controlling cases, statutes,
  and regulations, maps the citation network and the statutory landscape, and
  confirms everything is still good law. Thorough by default, and scales from a
  quick "what's the law on X" to a full doctrinal map. (Replaces the older
  separate case-law standard/deep and statute-research skills.)
  Download: [`dingduff_legal-research_v2.4.skill`](https://github.com/DingDuff/dingduff-public/blob/HEAD/dist/dingduff_legal-research_v2.4.skill)

### Legal analysis

- **`dingduff-legal-analysis`** (v1.2) — the reasoning engine. Frames the legal
  issues, synthesizes the governing rule from the cases and statutes you've
  gathered, analyzes the facts against the rule, organizes the proof
  (CRAC/CREAC), and deploys authority. Use when you want Claude to think
  through a question rigorously — *"what's the law on X," "do we have a claim,"
  "will this argument hold up," "what are the issues here."* Pairs with
  `dingduff-legal-research`, which gathers the authority it reasons over.
  Download: [`dingduff_legal-analysis_v1.2.skill`](https://github.com/DingDuff/dingduff-public/blob/HEAD/dist/dingduff_legal-analysis_v1.2.skill)

### Citation checking

- **`dingduff-citation-check`** (v2.5.8) — after you draft a memo (Markdown, **Word, or
  Google Docs**), verifies every citation against the opinion and statute files
  you saved **plus any other source you supply** — a Restatement section, a case
  missing from CourtListener, the other side's brief, a factual PDF — quality-checks
  that each highlighted passage is the on-point part of the source, and opens a
  review panel showing the memo and each source side by side. Runs entirely in
  your own session.
  Download: [`dingduff_citation-check_v2.5.8.skill`](https://github.com/DingDuff/dingduff-public/blob/HEAD/dist/dingduff_citation-check_v2.5.8.skill)
  Needs `python3` (Cowork and Claude Code provide it). Save case/statute sources
  first via `fetch_opinion_file` / `fetch_statute_file`; drop any other source (text or a
  text-layer PDF) into your working folder.
  How it works — reliability & privacy: see [How Citation Checking Works](Citation-Checking).

### Citation formatting

- **`dingduff-legal-citation-format`** (v1.4) — formats legal citations in
  practitioner / brief style (cases, statutes, signals like *see* / *cf.*,
  pincites, short forms, block quotes). Its rules follow *The Indigo Book* (a free, public-domain citation manual). It fixes *form only* — pair it with the
  research or cite-check skills to confirm an authority exists and is quoted
  accurately. Works on its own (no connector needed).
  It's a large skill, so Claude will usually run it in a subagent — that's
  expected and keeps your main chat fast.
  Download: [`dingduff_legal-citation-format_v1.4.skill`](https://github.com/DingDuff/dingduff-public/blob/HEAD/dist/dingduff_legal-citation-format_v1.4.skill)

## Install a single skill by hand

The plugin above is the easier path and covers every skill. If you'd rather
install just one, download its `.skill` file (on GitHub, open the file and use the
**Download raw file** button), then upload it to Claude — pick the row that
matches how you use Claude:

- **Cowork (desktop):** **Customize** (upper right) → **Skills** → upload the file.
- **claude.ai (browser):** **Settings → Capabilities → Skills** → upload the file.
- **Claude Code (CLI):** use the plugin instead — see above.

Skills installed this way don't update themselves; you'd re-download the file when
we ship a new version. That's the main reason we point people at the plugin.

> Skill files are named `dingduff_<skill>_vX.Y.skill`. In Claude's skill picker
> they appear under their `dingduff-…` name.

Once uploaded, the skill appears in the skill picker (the `/` menu). The research
skills trigger automatically when you ask a legal question; to cite-check, draft a
memo with DingDuff, then ask Claude to **"cite-check this memo."**

## Recommended Claude settings

### Always use DingDuff for legal research

Add a custom instruction so you don't have to ask every time:

1. Open **Profile → Instructions for Claude** (in your general settings).
2. Add something like:
   > *When I ask a legal question, always use the DingDuff connector and rely only
   > on the DingDuff database. Tell me the jurisdiction you searched and include
   > citations.*

### Turn off chat training (privacy)

In your Claude privacy settings, turn **off** the option that lets Claude train on
your chats. Recommended for confidential legal work.

## Tips for better results

When you ask a legal question, it helps to tell Claude to:

1. **Use only the DingDuff database** (so it doesn't pull from the open web) —
   handled automatically if you set the custom instruction above.
2. **Specify the jurisdiction** you want cases or statutes from.
3. **Ask for citations** in the answer.

Complex questions can take several minutes — that's normal while Claude researches.
