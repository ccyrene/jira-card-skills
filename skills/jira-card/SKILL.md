---
name: jira-card
description: One-command Jira card workflow for any project — `/jira-card "<what you did or want to do>"` creates a single well-formed card, resolving the board/project first, then sprint, due date, story points and priority from natural language plus a per-repo/folder config, asking (via a structured choice prompt) only when something is genuinely unclear. The same command routes by intent to backfill (cards from git commits), implement (pick up a backlog card and build it), browse (list To-Do cards), setup (project config), and list (show every command). First run in a repo auto-discovers everything into `.claude/jira-config.json` via the Atlassian MCP, asking at most one question — no hardcoded instance IDs; conventions ship as overridable defaults. Exactly one confirmation before any card is written; never transitions a card to Done without the user's explicit approval; never auto-commits code. All command words are lowercase. Trigger on `/jira-card`, `/jira`, `/jira-card list`, "สร้างการ์ด", "ทำ card", "post card", "backfill jira", "ปิด sprint", "เขียน card ย้อนหลัง", "ดึงการ์ด", "ทำ backlog", "ดู backlog", "อันไหนจะทำ", "implement card", "pickup card", "ตั้งค่า jira", "setup jira", "มีคำสั่งอะไรบ้าง", and proactively when a repo's commits have outrun the Jira board, or the user starts work matching an open To-Do card.
---

# jira-card

One skill, five card modes plus `list`. Figure out which one the user wants, read
its reference file, follow it. Route from what they said — don't make them pick.
**All command words are lowercase:** `create` `backfill` `implement` `browse`
`setup` `list`.

| User says / types | Command | Read first |
|---|---|---|
| `/jira-card "<desc>"`, "สร้างการ์ด …", "ทำ card เรื่อง X" — **the default** | **`create`** — one card from a description (board first → ask if unclear → full draft) | `reference/create.md` |
| "ทำ card จาก commit", "post card ย้อนหลัง", "ปิด sprint" — or commits outran the board | **`backfill`** — cards from git history, closed as Done | `reference/backfill.md` |
| "ดึงการ์ดมาทำ", "ทำ backlog", "อันไหนจะทำ", `/jira-card implement PROJ-123` | **`implement`** — pick a To-Do card, build it, move it across the board | `reference/implement.md` |
| "ดู backlog", "มี card อะไรบ้าง" | **`browse`** — list candidate cards, stop there | `reference/implement.md` (steps 1–2 only) |
| "ตั้งค่า jira", "เปลี่ยน project", or a field/transition error | **`setup`** — (re)discover the project config | `reference/setup.md` |
| "list", "help", "มีคำสั่งอะไรบ้าง", `/jira-card list` | **`list`** — print every command + its params, then stop | `reference/list.md` |

A bare `/jira-card <description>` → **`create`**. `/jira-card` with no
description, or a genuinely ambiguous ask → ask once (structured), offering the
commands. `/jira-card list` just prints the help and stops.

## Config — load it, or create it on the fly

Everything project-specific lives in one file, **per repo (or per folder)**:

```bash
cat "$(git rev-parse --show-toplevel)/.claude/jira-config.json"
```

**If it's missing, do not stop and do not tell the user to run setup.** Read
`reference/setup.md`, discover the config yourself (it asks at most one
question — usually none), write the file, then continue with whatever the user
originally asked, in the same turn. And if the `mcp__atlassian__*` tools don't
exist at all, `reference/setup.md` offers to install the Atlassian MCP (the user
authenticates once, then re-runs) — don't dead-end there either.

In the reference files, `<project.key>`, `<fields.storyPoints>`,
`<transitions.done>` etc. mean "that value from the config". Schema:
`reference/config-schema.md` · filled example: `config.example.json` ·
example instance IDs: `reference/profile-example.md`.

## Ground rules — every mode

- **One confirmation before writing.** Prepare everything, show one draft, get
  one go-ahead, then make all the Jira calls without further questions.
- **`create` may ask once when unsure.** It's the one mode that may ask a single
  batched round of questions *before* the gate — only when a card can't be
  written well from what's given (which board, vague summary, unresolved
  sprint/date, a required field with no default). Ask via the structured choice
  UI (`AskUserQuestion`), not prose; never guess; never make it an interrogation.
- Two safety gates that always stay: a card only reaches **Done** on the user's
  explicit approval (`implement` mode), and code is **never auto-committed**.
- Assignee is the live `currentUser()` — never store or hardcode a person.
- Every field/transition ID comes from the config. If Jira rejects one
  ("unknown field", "invalid transition"), refresh via `reference/setup.md` —
  don't guess IDs.
- Cards are written for engineers, in the config's `conventions.summaryStyle`.
- **MCP cost hygiene.** Every Jira read passes only the `fields` it needs (never
  the default set — omit `description` unless the step uses it), a tight
  `maxResults`, and `responseContentFormat: "markdown"`. Resolve `accountId`,
  sprint id, and config once per run and reuse them; never `getJiraIssue` right
  after an `editJiraIssue` (the edit already echoes the issue).

## When NOT to use

- Board administration (sprint dates, moving epics, archiving) → Jira UI.
- Work that has neither commits nor a description yet — there's nothing to write
  a card from. (A described idea *is* enough: that's `create`.)
