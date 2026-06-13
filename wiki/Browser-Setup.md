<!--
INSTRUCTIONS FOR CLAUDE
This page is for users running Claude in a web browser (claude.ai / claude.com)
instead of the desktop app. First make sure they completed the main install on
the [Home](Home) page. The key extra requirement in a browser is enabling
Claude's code-execution / sandbox ("virtual machine") capability with network
access turned on — otherwise the opinion_store / statute_store tools and the
cite-check skill cannot download or process files. If they can use the desktop
app instead, recommend that; Cowork on desktop is the most reliable environment.
-->

# Browser Setup

You can use DingDuff in a web browser at **claude.ai / claude.com**. The
connector setup is the same as on the desktop app — follow [Install
DingDuff](Home) first. This page covers the **one extra thing browsers need**.

> **Recommendation:** if you can install the Claude **desktop app** and use
> **Cowork** mode, do that instead — it's the smoothest experience and already
> includes the environment DingDuff's download and citation-check features rely
> on. Use the browser only if the desktop app isn't an option for you.

## Turn on Claude's code-execution environment ("virtual machine")

Most DingDuff research tools (searching cases, viewing opinions, statutes, PACER
dockets) work in the browser with no extra setup. But two kinds of work need
Claude to have a **sandboxed working environment** — sometimes described as
Claude using a "virtual machine":

- **Saving sources to files** — the `opinion_store` and `statute_store` tools
  hand Claude time-limited download links, and Claude needs a working environment
  (with internet access) to actually fetch and save those files.
- **The citation-check skill** (`dingduff-citation-check`) — it runs a small
  `python3` step locally in that environment.

### How to enable it

1. In Claude, open **Settings → Capabilities**.
2. Turn on the setting that lets Claude **run code and create files** (commonly
   labeled **"Code execution and file creation"**).
3. Turn on **internet access for that environment** — commonly labeled
   **"Allow network egress."** Without this, downloads silently fail.
4. Start a **new chat** afterward — these settings usually take effect only on
   new sessions, not the one you already have open.

> Anthropic occasionally renames these toggles. If you don't see the exact labels
> above, look under **Settings → Capabilities** for anything about **code
> execution**, an **analysis / sandbox environment**, or **network / internet
> access**, and turn those on. If you're on a Team or Enterprise plan, these may
> be controlled by your admin — see [Team & Enterprise](Team-and-Enterprise).

## Verify

1. Start a fresh chat with DingDuff connected.
2. Ask: *"Use DingDuff to find one Texas Supreme Court opinion on the economic
   loss rule, then save it to a file with `opinion_store`."*
3. If the file is created and Claude can read it back, the environment is set up
   correctly. If the tool "runs" but no file appears, see
   [Troubleshooting → Opinion/statute store tools don't work](Troubleshooting).

## What's different from the desktop app

- The connector itself works the same — same URL (`https://app.dingduff.com/mcp`),
  same sign-in.
- Plain research (search/view) works without the code-execution environment.
- File downloads and citation-checking **require** the code-execution environment
  above; on the desktop app's Cowork mode this is already available.
