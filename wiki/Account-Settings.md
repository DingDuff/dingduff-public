<!--
INSTRUCTIONS FOR CLAUDE
This is the "optimal setup" page: how to configure a Claude account so DingDuff
does its deepest research. The single most important idea is the three-tier
ladder — Claude answers legal questions best when it can use `fetch_opinion_file`
(Tier 1), acceptably with `opinion_extract` (Tier 2, needs a BYOK API key), and
least well with `opinion_view` (Tier 3). The right settings depend on the user's
Claude account type, so branch them early:
  - Personal (Pro/Max): they control their own settings — walk them through the
    four toggles, then the folder step.
  - Team/Enterprise: an admin controls the settings — give them the request to
    send, and offer BYOK as the fallback if the admin won't enable network egress.
Everyone, regardless of account, finishes with the two shared steps (install the
plugin, add the standing instruction). Be patient, one step at a time; the user
is probably a lawyer, not an engineer. Assume they have already installed and
signed into DingDuff (see the Home page) — this page is only about settings.
-->

# Account Settings for Optimal Use

DingDuff is only as strong as the tools you let Claude reach. A five-minute setup
is the difference between **benchmark-grade research** and a quicker, shallower
answer — and the right steps depend on **which kind of Claude account you have.**

> This page assumes you've already installed DingDuff and signed in. If not,
> start with [Install DingDuff](Home) first.

---

## How DingDuff researches your question

When you ask a legal question, DingDuff can work in three ways. Your settings
decide which one Claude is able to use.

| | Tool | What happens |
|---|---|---|
| **1 — Best** *(benchmark-grade)* | `fetch_opinion_file` | Claude saves the full text of each opinion to a folder on your computer and reads the source itself. This is exactly how DingDuff runs in our benchmark tests. |
| **2 — Good backup** | `opinion_extract` | Claude pulls the most relevant passages from each opinion. Needs your own Anthropic API key (BYOK) — a dependable backup for when Tier 1 isn't available. |
| **3 — Fallback** | `opinion_view` | Claude reads cases directly in the chat. You still get an answer — just a less thoroughly researched one. |

**The goal of this guide is simple:** get Claude to operate in **Tier 1**, with
**Tier 2** set up as an automatic backup. **Tier 3 is the least optimal version
of DingDuff.**

---

## Which Claude account do you have?

This decides who controls the settings DingDuff needs.

- **Personal — Pro or Max:** you control your own settings, so you can switch on
  everything Tier 1 needs yourself. → [Path A](#path-a--personal-pro-or-max)
- **Teams or Enterprise:** some settings are held by your organization's admin.
  You may need to send a short request — we've written it for you. →
  [Path B](#path-b--teams-or-enterprise)

Whichever you have, everyone finishes with the same
[two steps](#final-two-steps-that-everyone-needs) at the end.

---

## Path A — Personal (Pro or Max)

Four settings, all in your own control. These let Claude use `fetch_opinion_file`
to save and read full opinions.

1. **Turn on code execution** — lets Claude do the work of saving and reading
   files.
   `Settings → Capabilities → Code execution: ON`

2. **Turn on network egress** — lets Claude reach out and download each opinion.
   Without it, downloads silently fail.
   `Settings → Capabilities → Network egress: ON`

3. **Turn off Cloud to keep tasks on your computer** — so Claude runs locally,
   right where your connected folder lives (next step).
   `Cowork → Run new tasks in the cloud: OFF`

4. **Connect a folder each time you start a new CoWork chat.** Claude saves each
   opinion as an `.md` file in that folder, then reads it back. This is what makes
   `fetch_opinion_file` work — and it lets DingDuff research *more*, not less. If
   it isn't attached to a folder, it should save them in a virtual machine, but
   attaching a folder is the best way to ensure it uses this tool.

> Next: set up the [BYOK backup](#recommended-backup-byok-byo-api-key) and the
> [two steps everyone needs](#final-two-steps-that-everyone-needs).

---

## Path B — Teams or Enterprise

On a work plan, these settings live in your organization's controls. Ask your
admin for three things:

1. **Approve the DingDuff connector** — add DingDuff to the organization's list of
   approved connectors.
2. **Turn on network egress** — lets Claude download the full text of opinions.
3. **Allowlist the DingDuff domain** — where the setting says *"package managers
   only,"* add `app.dingduff.com` to the allowlist.

**Copy-and-send request for your admin:**

> Hi — I'd like to use DingDuff (a legal-research connector) inside Claude. Could
> you please, in our organization settings:
>
> 1. Add the DingDuff connector to our approved connectors.
> 2. Turn ON network egress.
> 3. Add `app.dingduff.com` to the allowlist (where it says "package managers only").
>
> Thank you!

**Can't get admin approval?** Set up the [BYOK backup](#recommended-backup-byok-byo-api-key)
below on your own. It unlocks `opinion_extract` (Tier 2) — noticeably better
results than going without, for roughly **$5–15/month** paid to Anthropic.

---

## Recommended backup: BYOK (BYO-API Key)

**Tier 2 (as a backup).** Adding your own Anthropic API key to your DingDuff profile unlocks
`opinion_extract` (Tier 2), so DingDuff has somewhere to fall back to if
`fetch_opinion_file` ever isn't available. The earliest version of DingDuff ran
entirely this way.

> **Typical cost, even with heavy research: $5–15/month, billed by Anthropic.**

**How to set it up:**

1. Create an API key in the **Anthropic Console** (add a payment method first).
2. Open your profile at **dingduff.com/profile**.
3. Paste the key in and save.

**Two safety rules (required by our [Terms](https://dingduff.com/terms)).** We've
implemented safety measures to protect your API key, but the internet is full of
bad actors. We require all our users to:

1. **Use an API key unique to DingDuff.** If anything ever looks off, you can
   deactivate that one key instantly — without touching anything else.
2. **Turn off auto-reload.** So you can never be hit with an unexpected large
   charge.

---

## Final two steps that everyone needs

Whichever account you have, finish with both of these.

1. **Install the DingDuff plugin.** It bundles the connector with the skills that
   drive it. In Claude: **Customize → Plugins → Add marketplace**, add the
   repository `DingDuff/dingduff-public`, then install the **dingduff** plugin.
   (See [Skills & Settings](Skills) for more.)

2. **Add one standing instruction.** Paste this into
   **Settings → General → Instructions** so you never have to ask twice. This
   instruction is important for ensuring that Claude grabs for the
   `fetch_opinion_file` tool:

   > Always use DingDuff when you need to access primary legal sources. When you
   > use DingDuff for primary legal sources, always use the
   > `dingduff-legal-research` skill from the DingDuff plugin.

---

## Confirm it's working

Start a fresh chat and ask Claude:

> Use DingDuff to find one Texas Supreme Court opinion on the economic loss rule
> and save it with `fetch_opinion_file`.

If a file lands in your connected folder and Claude reads it back to you, you're
fully set up — DingDuff is now doing its deepest research.

---

Questions? **hello@dingduff.com**
