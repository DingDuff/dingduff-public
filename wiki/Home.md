<!--
INSTRUCTIONS FOR CLAUDE (read this first)

You are helping a lawyer install and run DingDuff, a legal-research connector for
Claude. The user is probably not technical. Be patient, do one step at a time,
and confirm each step worked before moving to the next.

DingDuff is listed in Claude's connectors directory, so installing it is just
"find it in the directory and click add" — there is no URL to paste and no
"custom connector" dialog. Don't send the user looking for one.

Do this:
1. Ask whether they already have a DingDuff account (dingduff.com). They need one
   before connecting, because connecting asks for that email and password.
2. Ask which environment they use:
   - The Claude desktop app (Mac/Windows) — RECOMMENDED, especially Cowork mode.
   - A web browser at claude.ai / claude.com.
   - The mobile app — connecting works, but downloads/cite-check don't; see the
     "Using DingDuff on mobile" section and steer them to desktop/browser for full
     features.
3. Walk them through "Install DingDuff" on this page, step by step. The fastest
   route is the direct listing link in Step 2; the in-Claude route is right below
   it if the link doesn't open for them.
4. Branch as needed:
   - Browser user → also read the [Browser Setup](Browser-Setup) page.
   - On a Team or Enterprise plan and the DingDuff card shows "Request" instead of
     an add button, or connectors are managed by their admin →
     read [Team & Enterprise](Team-and-Enterprise).
   - A tool fails or behaves oddly → read [Troubleshooting](Troubleshooting) and
     match the symptom.
   - They want the optional skills and best-practice settings → read [Skills & Settings](Skills).
   - On a locked-down account where they CAN'T enable Claude's code execution /
     network egress (so `fetch_opinion_file` can't save files) → point them to the
     "BYOK / API key (Legacy)" section below.
5. The DingDuff listing in the directory:
   https://claude.ai/directory/connectors/74942e30-fba3-4cfd-a381-75cf6a779c83

Verify success at the end by asking the user to have Claude confirm it can see
the `opinion_search` tool — that means the connector is connected and working.
-->

# DingDuff Installation & Help

DingDuff is a **legal-research connector for Claude**. It links your own Claude
account to a database of millions of court opinions, federal and state statutes
and rules, and federal court filings (PACER) — so you can do real legal research
right inside Claude, with citations.

DingDuff is listed in **Claude's connectors directory**, so adding it takes about
a minute: find DingDuff in the directory, click add, sign in.

This wiki is written so you can either **read it yourself** or **point Claude at
it** and ask Claude to walk you through everything. The easiest path:

> Open Claude, paste the link to this page, and say:
> *"Walk me through installing DingDuff, one step at a time."*

## Pages in this wiki

- **Install DingDuff** (this page) — the main setup, start to finish.
- [DingDuff with ChatGPT (beta)](ChatGPT) — how to connect DingDuff to ChatGPT instead of Claude (in beta; Claude is the primary, fully-supported experience).
- [Browser Setup](Browser-Setup) — extra steps if you use Claude in a web browser instead of the desktop app.
- [Team & Enterprise](Team-and-Enterprise) — what to do if you're on a work plan and your admin controls connectors.
- [Troubleshooting](Troubleshooting) — fixes for common problems (a tool isn't working, you can't sign in, etc.).
- [Skills & Settings](Skills) — optional add-ons that make DingDuff noticeably better.
- [How Citation Checking Works](Citation-Checking) — what the cite-checker does, and the design behind its reliability and privacy.

---

## Before you start

DingDuff itself is **free while in beta**. To use it you need two things:

1. **A DingDuff login** — sign up at **https://dingduff.com** to create your
   account. This gives you the email + password you'll use when connecting.
   DingDuff is for **licensed attorneys** (per the Terms of Service).
2. **Your own Claude account** — a paid plan (Pro, Max, Team, or Enterprise) is
   recommended. The Claude **desktop app** with **Cowork** mode is the best
   experience; a web browser also works (see [Browser Setup](Browser-Setup)).

> Create the DingDuff account **first**. Step 2 below asks you to sign in with it,
> so having it ready keeps the install to one pass.

---

## Install DingDuff

### Step 1 — Sign up at dingduff.com

Go to **https://dingduff.com**, click **Sign Up**, and create your account. Keep
that email and password handy.

### Step 2 — Add DingDuff from Claude's connector directory

**The quick way:** open the DingDuff listing and click the add button:

> **https://claude.ai/directory/connectors/74942e30-fba3-4cfd-a381-75cf6a779c83**

**Or find it inside Claude:**

1. In Claude, open **Customize** from the left sidebar (in a browser this may be
   under **Settings**), then go to **Connectors**.
2. Click the **+** button, then choose **Browse connectors**. The **Directory**
   opens.
3. Make sure **Connectors** is selected on the left, then type **DingDuff** in the
   search box.
4. On the **DingDuff** card, click the **+** to add it.

Either way, Claude then sends you to the **DingDuff sign-in page**. Enter the
**email and password** for the account you created in Step 1 and approve the
connection. You'll be returned to Claude automatically.

> DingDuff is labeled a **Community** connector in the directory. That means it
> passed Anthropic's automated checks for the directory but wasn't individually
> reviewed by Anthropic — it works exactly like any other directory connector once
> connected.

> A small browser/login window normally opens for sign-in. If nothing appears,
> see "Sign-in window doesn't open" in [Troubleshooting](Troubleshooting).

> On a **Team** plan you may see **Request** instead of an add button — that means
> your admin controls connectors. Click it and see
> [Team & Enterprise](Team-and-Enterprise).

### Step 3 — Allow DingDuff's tools

After connecting, DingDuff appears in your connector list with its tools. We
recommend setting each tool to **always allow** (the **checkmark**, not the
hand icon) so you aren't asked for permission on every research request.

### Step 4 — Confirm it works

In a chat, ask Claude:

> *"Does the DingDuff connector have the `opinion_search` tool?"*

If yes, the connector is working. Now try a real query, e.g.:

> *"Using only DingDuff, find recent Texas appellate cases on the economic loss
> rule and give me citations."*

---

## BYOK / API key — *(Legacy)*

**Most users don't need this — skip it unless you're in a locked-down environment
(read on).**

DingDuff works best when Claude can **save the full text of a case or statute to
your working folder** with `fetch_opinion_file` / `fetch_statute_file` and read the actual
source. That needs Claude's **code-execution environment with network access**
turned on (Settings → Capabilities → *Code execution and file creation* +
*Allow network egress*; the desktop **Cowork** app already has it — see
[Browser Setup](Browser-Setup)).

The **BYOK** (bring-your-own-key) path is for when you **can't turn those settings
on** — e.g. a corporate **Team / Enterprise** account whose admin won't enable code
execution or network egress. Without those, the store tools can't download files,
so instead you add **your own Anthropic API key** to your DingDuff profile. That
unlocks three tools that run on DingDuff's back end — `opinion_extract`,
`submit_batch_screen`, and `retrieve_batch_screen` — which hand Claude **focused
excerpts** of the relevant material, so it can read what matters **without
downloading anything and without flooding the chat** with full opinions.

**Which one applies to you?**

- **You can change Claude's settings** (most Pro/Max users; Cowork desktop) → turn
  on code execution + network egress and use `fetch_opinion_file` / `fetch_statute_file`.
  Better results, no key needed. **Skip BYOK.**
- **You can't change those settings** (locked-down work account) → set up BYOK:
  1. Get an Anthropic API key from the **Claude Console** (console.anthropic.com)
     — add a payment method and create a key (ask Claude to walk you through it).
  2. Log in to your **profile on dingduff.com** and paste the key in.
  3. Use a **dedicated** key and **turn off auto-reload** (required by our Terms).

> Cost is small — typically a few dollars a month, billed by Anthropic, not DingDuff.

---

## Recommended settings (optional but worth it)

These take a few minutes and noticeably improve results. Full details on
[Skills & Settings](Skills):

- **Install the `dingduff-legal-research` skill** — it improves the quality and
  depth of research answers.
- **Install the `dingduff-legal-analysis` skill** — the reasoning step that
  frames the issues and organizes the proof from a research answer.
- **Install the `dingduff-citation-check` skill** — verifies every citation in a
  drafted memo against the stored sources.
- **Add a custom instruction** (Profile → *Instructions for Claude*) telling
  Claude to always use DingDuff for legal research, so you don't have to ask each
  time.
- **Turn off chat training** in your Claude privacy settings.

---

## Using DingDuff on mobile

You can add the DingDuff connector on the **Claude mobile apps** the same way —
the connectors directory is available there too — and **research tools** (searching
and viewing cases, statutes, and PACER) work fine.

However, the features that need a working file environment — **saving sources**
(`fetch_opinion_file` / `fetch_statute_file`) and the **citation-check** skill — rely on the
desktop app or browser. For full functionality, use the **desktop app (Cowork)**
or a **browser**; treat mobile as read-and-research on the go.

## Quick fixes

- **A DingDuff "store" tool says it worked but no files appear** → you likely
  need to turn on network access for Claude's tools. See
  [Troubleshooting → Opinion/statute store tools don't work](Troubleshooting).
- **DingDuff doesn't show up when you search the directory** → see
  [Troubleshooting → You can't add DingDuff from the directory](Troubleshooting).

For everything else, see [Troubleshooting](Troubleshooting).
