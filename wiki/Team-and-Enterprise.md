<!--
INSTRUCTIONS FOR CLAUDE
This page is for users on a work Claude account (Team or Enterprise). DingDuff is
in Claude's connectors directory, so there is no URL for an admin to paste — the
admin just enables the DingDuff listing for the organization. The common blocker:
the member's role doesn't allow enabling connectors, so the DingDuff card shows
"Request" instead of an add button. Help them send the request and give their
admin the exact steps. Also covers org-level network/code settings an admin may
need to enable.
-->

# Team & Enterprise Plans

On **Team** and **Enterprise** Claude plans, connectors are often controlled by your
organization. If your role doesn't allow enabling connectors, you can't add DingDuff
yourself — an admin enables the DingDuff listing for the organization first, and
then each member connects individually with their own DingDuff login.

## How to tell this is your situation

Any of these usually means it's an admin/organization setting, not something you
did wrong:

- In the directory, the **DingDuff** card shows a **Request** button instead of a
  **+** / **Connect** button.
- DingDuff doesn't appear in the directory for you even though a colleague has it.
- You see a message that the connector isn't available for your organization or
  your role.

## Ask for it with the Request button

On a Team plan, clicking **Request** on the DingDuff card sends it to your
organization's admins for review — the button then reads **Requested** while it's
pending. Claude shows you the outcome the next time you open the directory.

That's usually all you need to do. If you'd rather reach your admin directly, send
them the steps below.

## What an admin needs to do (send them this)

> Please enable the DingDuff connector for our organization:
> 1. Go to **Admin Settings → Connectors** (claude.ai/admin-settings/connectors).
> 2. Find **DingDuff** — it's in Claude's connectors directory, so there's no URL to
>    enter. If I've already requested it, it's under **Requested by your team** at the
>    top of the list; otherwise search the directory for it.
> 3. Enable it for the organization.
> 4. Make sure my role is allowed to use connectors (not "Blocked").
>
> DingDuff is a free legal-research connector; each of us signs in with our own
> DingDuff account (dingduff.com), so there are no shared credentials.

Once the admin has enabled it, each member connects on their own:

1. Open **Customize → Connectors** (or **Settings → Connectors**).
2. Find **DingDuff** and click **Connect**.
3. Sign in with your **DingDuff** email and password (from dingduff.com).

Then continue with [Install DingDuff → Step 3](Home) (allow the tools).

## If the connector connects but tools are blocked

On Enterprise plans, roles can allow a connector but restrict individual tools.
If some DingDuff tools are missing or always blocked, ask your admin to set
DingDuff's tools to **Always allow** (or at least "Ask") for your role, rather
than **Blocked**.

## Code execution & network access (for downloads and citation-check)

DingDuff's `fetch_opinion_file` / `fetch_statute_file` tools and the citation-check skill
need Claude's **code-execution environment with internet access** (see
[Browser Setup](Browser-Setup) for what this is). On Team/Enterprise plans this
is often controlled centrally. If downloads fail, ask your admin:

> Please enable code execution / file creation and **allow network egress** for
> our organization under **Admin Settings → Capabilities**, so DingDuff can
> download legal sources and run citation checks.

Note: capability changes usually apply only to **new** chat sessions.

**If your admin won't (or can't) enable those**, you can still use DingDuff via
the **BYOK / API key (Legacy)** path — add your own Anthropic API key to your
dingduff.com profile to turn on back-end tools (`opinion_extract`,
`submit_batch_screen`, `retrieve_batch_screen`) that let Claude read case material
without downloading anything. See [Install → BYOK / API key](Home).

## Still stuck?

See [Troubleshooting](Troubleshooting), or email **hello@dingduff.com** with your
plan type (Team or Enterprise) and what you see on the Connectors screen.
