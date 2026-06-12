# DingDuff Plugins

Claude Code / Cowork plugin marketplace for [DingDuff](https://dingduff.com)
legal-workflow skills.

## What's here

- **`dingduff`** — DingDuff legal workflow skills. Currently bundles:
  - **`dingduff-citation-check`** — after you draft a legal memo with the
    DingDuff MCP tools, verifies every citation against your locally stored
    opinion and statute files and opens an attorney review panel showing the
    memo and each cited source side by side, with the supporting passages
    highlighted. Verification runs entirely in your own Claude session.

## Requirements

- The **DingDuff MCP connector** must be added to your Claude client (the skill
  uses DingDuff's `opinion_store` / `statute_store` tools and the
  `citecheck_review` review panel).
- `python3` on the machine running the session (Cowork and Claude Code both
  provide this) — the verifier runs as a local script.

## Install

### Claude Cowork

Open **Customize → Skills**, add this marketplace
(`DingDuff/dingduff-plugins`), and install the **dingduff** plugin. The
`/dingduff:dingduff-citation-check` skill then appears in the skill picker.

### Claude Code (CLI)

```
/plugin marketplace add DingDuff/dingduff-plugins
/plugin install dingduff@dingduff
```

## Updates

```
/plugin marketplace update dingduff
```

## Source

The skill is developed in the DingDuff MCP server repository and vendored here
for distribution.
