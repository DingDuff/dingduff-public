<!--
This is the ChatGPT connection page. DingDuff's primary, fully-supported platform
is Claude (see Home). ChatGPT support is in BETA. Keep this page consumer-facing:
walk the user through turning on Developer mode and adding the connector. Do NOT
explain the technical/auth internals. The connector URL for ChatGPT is exactly
https://app.dingduff.com/mcp-chatgpt/ (note the trailing /mcp-chatgpt/). ChatGPT is
the one place a URL still gets pasted by hand — on Claude, DingDuff installs from
the connectors directory instead. Reassure the user that a "Disconnected" label is
normal.
-->

# DingDuff with ChatGPT (Beta)

> **⚠️ DingDuff for ChatGPT is in beta.** It works, but it's newer and rougher than
> our Claude experience, which is our primary, fully-supported platform. If DingDuff
> is part of your daily workflow, we recommend Claude — see [Home / Install](Home).
> Use these steps if you'd like DingDuff inside ChatGPT and are comfortable with a
> beta.

DingDuff is a **legal-research connector**: it links your ChatGPT to millions of
court opinions, federal and state statutes and rules, and federal court filings
(PACER), so you can do real legal research inside ChatGPT, with citations.

---

## Before you start

You need three things:

1. **A paid ChatGPT plan — ChatGPT Work works best.** Adding a custom connector
   requires ChatGPT's **Developer mode**, available on paid plans (**Plus, Pro,
   Business, Enterprise, Edu**). DingDuff works **best in ChatGPT Work** (the plan
   for teams/business) — it's the smoothest experience and it's what unlocks
   **Skills** (see the optional skills section near the bottom of this page). The
   free plan can't add the connector.
2. **ChatGPT in a web browser.** Developer mode is only available at
   **chatgpt.com** in a browser — not in the mobile app.
3. **A DingDuff login.** Sign up at **https://dingduff.com** (click **Sign Up**) to
   create your account — you'll use that email and password when connecting.
   DingDuff is for **licensed attorneys** (per the Terms of Service).

> If you haven't created a DingDuff account yet, do that first at
> https://dingduff.com. You'll need that email and password during Step 3.

---

## Step 1 — Turn on Developer mode

1. Open ChatGPT in a **web browser** at **chatgpt.com**.
2. Go to **Settings**, then **Connectors** (some accounts label this
   **Apps & Connectors**).
3. Open **Advanced settings** and turn on **Developer mode**.

> Developer mode is what lets ChatGPT add a custom connector like DingDuff. If you
> don't see the option, double-check you're on a **paid plan** and using ChatGPT in
> a **browser** (not the mobile app).

## Step 2 — Add the DingDuff connector

1. Still under **Settings → Connectors**, click **Create** (or the **+** /
   **New connector** button).
2. Give it a name, e.g. `DingDuff`.
3. In the **URL** field (sometimes called *MCP Server URL*), paste exactly:

   ```
   https://app.dingduff.com/mcp-chatgpt/
   ```

   > Copy it exactly, including the ending **`/mcp-chatgpt/`**. This is a **different
   > address** from the Claude connector — using the Claude URL here won't work.

4. For authentication, choose **OAuth**.
5. Click **Create** (or **Connect**).

## Step 3 — Sign in to DingDuff

ChatGPT will send you to the **DingDuff sign-in page**. Enter the **email and
password** for the DingDuff account you created at dingduff.com, and approve the
connection. You'll be returned to ChatGPT.

---

## Step 4 — About the "Disconnected" label — *(read this!)*

After connecting, ChatGPT may show the connector as **"Disconnected."**

> **This is normal and does NOT mean it's broken.** In ChatGPT's developer mode, a
> connector often shows "Disconnected" simply because it isn't being used at that
> exact moment — ChatGPT connects to it when it actually needs it during a chat.
> DingDuff still works.

So don't keep removing and re-adding the connector trying to make it say
"Connected." Instead, just **test it with a real question** (next step).

## Step 5 — Confirm it works

Start a **new chat** and ask ChatGPT to use DingDuff, for example:

> *"Using the DingDuff connector, find recent Texas appellate cases on the economic
> loss rule and give me the citations."*

If ChatGPT runs DingDuff's tools and comes back with cases and citations, you're
set — **even if the connector still shows "Disconnected."**

> The first time DingDuff's tools run, ChatGPT may ask you to approve them. Approve
> them (you can choose to remember the choice for that conversation).

---

## What works in ChatGPT

The core research tools work well: **searching and reading** court opinions,
statutes, and rules, and **searching PACER**.

A couple of DingDuff features are built specifically for Claude and won't behave
the same in ChatGPT — the interactive **citation-check review panel** and **saving
source files** to a working folder. For those, use Claude (see [Home](Home)).

---

## Add DingDuff's skills (optional)

DingDuff's optional **skills** — extra instruction sets that make research,
analysis, and citation work noticeably better — also work in ChatGPT. They're the
**same skills** described on [Skills & Settings](Skills), and they use a skill
format ChatGPT understands, so **you don't need Claude installed** to use them.
Skills are a **ChatGPT Work** feature — another reason DingDuff works best there.

To add a skill:

1. **Download the skill file(s)** from the [Skills & Settings](Skills) page — on
   GitHub, open a `.skill` file and click **Download raw file**. The files are
   named like `dingduff_legal-research_v2.4.skill`.
2. A `.skill` file is just a **zipped folder**. If ChatGPT accepts the `.skill`
   directly, use it as-is; if it doesn't, **rename it to end in `.zip` and unzip
   it** to get the skill **folder** (the folder contains a `SKILL.md` file).
3. In the **ChatGPT desktop app**, open **Skills**, then choose **Create →
   Upload from your computer** and select the skill (the `.skill`/`.zip`, or the
   unzipped folder). ChatGPT scans it, and it's available a moment later.
4. **Repeat** for each skill you want. If a skill doesn't appear right away,
   restart ChatGPT.

> If you don't see a **Skills** area or the upload option, you're most likely not
> on **ChatGPT Work** — skills are a Work/Business feature.

Once added, the research skills kick in when you ask a legal question; to
cite-check, draft a memo with DingDuff, then ask ChatGPT to *"cite-check this
memo."*

---

## Trouble?

- **No "Developer mode" option** → confirm you're on a **paid plan** and using
  ChatGPT in a **web browser** (developer mode is web-only).
- **The sign-in page didn't open, or the connection didn't finish** → remove the
  connector and add it again, making sure the URL is **exactly**
  `https://app.dingduff.com/mcp-chatgpt/`.
- **It says "Disconnected"** → that's expected — see **Step 4**. Judge it by whether
  a real query works, not by the label.
- **ChatGPT won't use DingDuff in a chat** → ask it directly, e.g. *"Use the
  DingDuff connector to …"*, and approve the tools when prompted.

Still stuck? Email **hello@dingduff.com**.
