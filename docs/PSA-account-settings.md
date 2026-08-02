# PSA — Set your Claude account up for optimal DingDuff research

*Short announcement to send to DingDuff users. The specifics match the
[Account Settings](../wiki/Account-Settings.md) wiki page and
[setup-guide.html](./setup-guide.html) word-for-word — if you edit one, edit all
three.*

---

**Subject: One 5-minute setting change = much better DingDuff research**

Hi there,

Quick but important PSA. Most DingDuff users never turn on the setting that lets
Claude do its *deepest* legal research — so they're getting a good answer, but not
the best one DingDuff can give.

Here's the short version. When you ask a legal question, DingDuff can work three
ways, best to worst:

1. **`fetch_opinion_file`** — Claude saves the full text of each opinion to a
   folder and reads the source itself. *This is how we run our benchmarks.*
2. **`opinion_extract`** — Claude pulls the most relevant passages. Needs your own
   Anthropic API key (BYOK). A solid backup.
3. **`opinion_view`** — Claude reads cases in the chat. Still an answer, just less
   thoroughly researched.

**The goal: get Claude to Tier 1, with Tier 2 as an automatic backup.** How you do
that depends on your Claude account:

**If you're on a personal account (Pro or Max)** — you can turn everything on
yourself:
- `Settings → Capabilities → Code execution: ON`
- `Settings → Capabilities → Network egress: ON`
- `Cowork → Run new tasks in the cloud: OFF`
- **Connect a folder each time you start a new CoWork chat** — this is what lets
  Claude save and re-read full opinions.

**If you're on a Teams or Enterprise account** — ask your admin to (1) approve the
DingDuff connector, (2) turn ON network egress, and (3) add `app.dingduff.com` to
the allowlist. If that's not possible, add your own Anthropic API key to your
DingDuff profile to unlock `opinion_extract` — about **$5–15/month** paid to
Anthropic, even with heavy use.

**Everyone should do two more things:**
- Install the **dingduff** plugin (Customize → Plugins → Add marketplace →
  `DingDuff/dingduff-public`).
- Paste this into `Settings → General → Instructions`:
  > Always use DingDuff when you need to access primary legal sources. When you
  > use DingDuff for primary legal sources, always use the `dingduff-legal-research`
  > skill from the DingDuff plugin.

Full step-by-step (including the recommended BYOK backup and its two safety
rules): **[Account Settings for Optimal Use](https://github.com/DingDuff/dingduff-public/wiki/Account-Settings)**

Thanks — and happy researching,
The DingDuff team
hello@dingduff.com
