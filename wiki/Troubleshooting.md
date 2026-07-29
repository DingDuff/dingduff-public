<!--
INSTRUCTIONS FOR CLAUDE
Match the user's symptom to one of the sections below and walk them through the
fix. Each entry is Symptom → Cause → Fix. The two most common real-world issues
are: (1) the opinion/statute store tools "not working" because network egress /
the code-execution environment is off, and (2) Team/Enterprise users who can't
add the connector because an admin must enable it. Confirm the fix worked before
moving on.

DingDuff installs from Claude's connectors directory (search "DingDuff" and click
add) — there is no URL to paste, so don't send users hunting for a "custom
connector" dialog or ask them to re-check a server URL.
-->

# Troubleshooting

Find the symptom that matches, then follow the fix. If a connector or capability
change doesn't seem to take effect, **start a new chat** — many settings only
apply to new sessions.

---

## Opinion/statute store tools don't work (no files appear)

**Symptom:** You ask Claude to save cases or statutes with `fetch_opinion_file` or
`fetch_statute_file`. The tool seems to run, but no files show up and Claude can't
read them back.

**Cause:** These tools return **time-limited download links**. Claude has to fetch
those links using its **code-execution environment**, and that environment needs
**internet access**. If code execution or network access is turned off, the
download silently fails.

**Fix:**
1. Open **Settings → Capabilities**.
2. Turn on **Code execution and file creation** (the setting that lets Claude run
   code / create files).
3. Turn on **Allow network egress** (internet access for that environment).
4. **Start a new chat** — these usually take effect only on new sessions.
5. Retry the save.

> Labels may vary. If you don't see those exact names, look under **Settings →
> Capabilities** for code execution / sandbox / network access and enable them.
> On Team/Enterprise this may be an admin setting — see
> [Team & Enterprise](Team-and-Enterprise). More detail in
> [Browser Setup](Browser-Setup).

> **Can't change these settings** (a locked-down work account)? Use the
> **BYOK / API key (Legacy)** path instead — an Anthropic API key on your
> dingduff.com profile enables back-end tools that read case material without
> downloading files. See [Install → BYOK / API key](Home).

---

## You can't add DingDuff from the directory

**Symptom:** You search the directory for DingDuff and there's no add button — or
the card shows **Request**, or DingDuff doesn't appear at all.

**Cause:** You're on a **Team/Enterprise** plan where your organization controls
connectors, or you're searching the wrong tab of the directory.

**Fix:**
- Make sure **Connectors** is selected in the directory's left sidebar (it also
  lists Skills and Plugins, and the search only shows the selected kind).
- Try the listing link directly:
  **https://claude.ai/directory/connectors/74942e30-fba3-4cfd-a381-75cf6a779c83**
- **Card shows "Request":** click it — that sends DingDuff to your admins for
  approval. See [Team & Enterprise](Team-and-Enterprise).
- **Team/Enterprise, nothing appears:** an admin must enable it for the
  organization. [Team & Enterprise](Team-and-Enterprise) has the exact steps to
  send them.

---

## The sign-in window doesn't open (OAuth/login)

**Symptom:** After adding DingDuff, no DingDuff sign-in page appears, or sign-in
never completes.

**Cause:** A popup blocker or privacy extension is blocking the login window, or
you don't yet have a DingDuff account.

**Fix:**
- Make sure you created a DingDuff account at **https://dingduff.com** first —
  connecting asks for that email and password.
- Allow popups for Claude, and disable ad/privacy blockers for the sign-in.
- Try a different browser, then re-add the connector.

---

## DingDuff is connected, but Claude doesn't use it

**Symptom:** DingDuff is in your connector list, but Claude answers legal
questions without it, or says it has no DingDuff tools in this chat.

**Cause:** The connector isn't toggled on for that chat, or its tools aren't
permitted.

**Fix:**
- In the chat, click the **+** (tools) control and make sure **DingDuff** is
  toggled **on**.
- In **Customize → Connectors → DingDuff**, set the tools to **always allow**
  (checkmark, not the hand).
- Tell Claude explicitly: *"Use only the DingDuff database for this."* Adding a
  custom instruction (see [Skills & Settings](Skills)) makes this automatic.

---

## It worked yesterday, now it asks me to sign in again

**Symptom:** DingDuff stops responding and you're prompted to reconnect.

**Cause:** Sign-in sessions expire periodically (about an hour of token validity),
which is normal.

**Fix:** Reconnect via **Customize → Connectors → DingDuff → Connect** and sign in
again. If it keeps happening immediately, remove and re-add the connector.

---

## The citation-check skill won't run

**Symptom:** `dingduff-citation-check` errors, can't find sources, or can't run.

**Cause:** It needs (a) `python3` available in the session and (b) your source
files saved locally first via `fetch_opinion_file` / `fetch_statute_file`.

**Fix:**
- Use **Cowork (desktop)** or **Claude Code**, which provide `python3`. In a plain
  browser chat, enable the code-execution environment ([Browser Setup](Browser-Setup)).
- First save the cited opinions/statutes with the store tools (which need network
  access — see the first entry above), then run the cite-check.
- See [Skills & Settings](Skills) for install steps.

---

## Still stuck

Email **hello@dingduff.com**. It helps to include: your plan (Free/Pro/Max/Team/
Enterprise), whether you're on the desktop app or a browser, the tool or step that
failed, and any error text Claude showed.
