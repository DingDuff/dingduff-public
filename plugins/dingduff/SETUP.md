# Setting up DingDuff

This plugin bundles the **DingDuff legal-research connector** (`dingduff`, a
remote MCP server at `https://app.dingduff.com/mcp`) along with the five skills
that drive it. Installing the plugin registers the connector; it does not sign
the user in. Walk the user through the steps below.

## 1. Confirm they have a DingDuff account

The connector requires one. It is free, and it is limited to licensed attorneys
under the [Terms of Service](https://dingduff.com/terms).

If they do not have an account, send them to **https://dingduff.com** to sign
up, and wait — authentication in step 2 will fail without it.

## 2. Authenticate

The connector uses OAuth 2.0. The user signs in through their browser; no API
key, token, or password is ever entered into Claude, and none should be
requested.

- **Claude Code:** have the user run `/mcp`, select `dingduff`, and follow the
  browser sign-in. The server shows `connected` when it succeeds.
- **Cowork / claude.ai:** the connector appears in the connector list and
  prompts for sign-in on first use.

Sign-in is a one-time step per machine; the session persists across restarts.

## 3. Verify the tools are live

Confirm the connection before relying on it:

> Does the DingDuff connector have the `opinion_search` tool?

A healthy connection exposes tools for case-law search and retrieval, statutes
and codes, PACER dockets and filings, and citation review. If the tool list is
empty or the server shows as failed, see Troubleshooting below.

## 4. Point them at the right skill

Four of the five skills depend on the connector:

| Skill | Needs the connector |
|---|---|
| `dingduff-legal-research` | yes |
| `dingduff-legal-analysis` | yes |
| `dingduff-validity-check` | yes |
| `dingduff-citation-check` | yes — plus `python3` |
| `dingduff-legal-citation-format` | no, works standalone |

The skills trigger on their own when the task fits. They can also be invoked
directly, for example `/dingduff:dingduff-validity-check`.

## Already had the connector installed?

Users who already added DingDuff — through the Anthropic connectors directory,
or by pasting `https://app.dingduff.com/mcp` into a custom connector — will now
have **two registrations of the same server**. Leave them alone. Everything
works, and on Cowork and claude.ai the connector is the registration holding the
sign-in, so removing it breaks a working setup.

Claude may also report that `plugin:dingduff:dingduff` needs authorization while
tool calls are succeeding. That is a known client-side bug
([claude-ai-mcp#727](https://github.com/anthropics/claude-ai-mcp/issues/727)),
not an account or install problem. Do not tell the user DingDuff is unavailable
on the strength of it — try a tool call and go by the result.

## Troubleshooting

- **Tools missing after sign-in** — run `/mcp` and check that `dingduff` reads
  `connected` rather than `failed` or `needs authentication`.
- **Sign-in loops or expires quickly** — have the user sign out and back in via
  `/mcp`; if it persists, that is a server-side session issue, so send them to
  support rather than retrying.
- **`python3` not found** during a cite-check — Claude Code and Cowork both
  provide it; a stripped environment may not.
- Anything else: the [installation and troubleshooting
  wiki](https://github.com/DingDuff/dingduff-public/wiki) covers browser setup,
  Team and Enterprise plans, mobile, and known failure modes.

## Privacy and terms

- [Privacy Policy](https://dingduff.com/privacy) — what the connector logs and
  retains
- [Terms of Service](https://dingduff.com/terms)
- [DingDuff Skills License 1.0](./LICENSE.md) — the license these skills ship
  under
- Support: [hello@dingduff.com](mailto:hello@dingduff.com)
