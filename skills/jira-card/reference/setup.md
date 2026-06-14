# Setup — discover the project once, write the config

Goal: fill `<repo-root>/.claude/jira-config.json` using the Atlassian MCP.
Schema: `config-schema.md` · filled example: `../config.example.json`. Config is
**per repo (or per folder)** — never user-global, so repos/folders targeting
different projects don't collide.

**Run quietly.** Ask the user only what cannot be inferred — usually nothing,
sometimes "which project?". Everything else is discovery + sensible defaults,
surfaced in one summary at the end where the user can object.

## Prerequisite — the Atlassian MCP (bootstrap it if missing)

Every mode needs the `mcp__atlassian__*` tools. If they're missing, don't
dead-end the user — offer to set the server up, then hand off the one part that
must be theirs (authentication).

1. **Ask once:** "ยังไม่เจอ Atlassian MCP — ให้ผมตั้งค่าให้ไหม?" On a yes:
2. **Register it** — `--scope project` writes a committable `.mcp.json` in the
   repo (the team shares the server entry; OAuth still authenticates per user):
   ```bash
   claude mcp add --transport http --scope project atlassian https://mcp.atlassian.com/v1/mcp/authv2
   ```
   Don't use `--scope user` — keep server + Jira config per repo/folder so
   different repos don't collide.
3. **Hand off what only the user can do** (say why: OAuth is a security boundary,
   and a just-added server isn't live until Claude Code reconnects):
   - approve the server when Claude Code prompts to trust it;
   - `/mcp` → `atlassian` → **Authenticate** (browser login);
   - re-run the original `/jira-card` request.
4. **Stop this turn** after the hand-off — the new tools won't appear
   mid-session, so continuing now would only fail. Resume when they're back,
   authenticated.

No `claude` CLI / restricted environment / user declines? Fall back to the plain
hard stop: ask them to connect it via `/mcp` → Atlassian.

If a config already exists and the user asked for a refresh, show the current
values, change what they asked, re-verify the rest.

## What to discover (read-only until the final write)

1. **Site + cloudId** — `getAccessibleAtlassianResources`. One site → take it.
   Several → ask which.
2. **User** — `atlassianUserInfo`. Used for JQL and the summary only. Never
   stored: the config says `"assignee": "currentUser"` so one committed file
   works for the whole team.
3. **Project** — first match wins: a key the user mentioned → the most frequent
   project in their recent cards (JQL `assignee = currentUser() OR reporter =
   currentUser() ORDER BY updated DESC`) → ask. Then `getVisibleJiraProjects`
   with the key → record `key`, `id`, `name`.
4. **Issue type** — `Task` from the project's issue types, unless the team
   clearly estimates on `Story`.
5. **Field IDs, resolved by NAME** — `getJiraIssueTypeMetaWithFields`. Walk
   `fields[]`, map human names to `customfield_*` keys:
   - "Story Points" (or "Story point estimate") → `fields.storyPoints`
   - "Sprint" (schema `gh-sprint`) → `fields.sprint`
   - "Team" (schema `atlassian-team`) → `fields.team`
   - "Due date" (system field, key literally `duedate`) → `fields.dueDate`
   Also capture every extra `required: true` field and its `allowedValues` —
   those must be supplied at create time (next step); one with no sensible
   default becomes a question Create mode asks before writing. A field that
   doesn't exist on this project → store `null`; the workflows skip it.
6. **Create-time defaults, copied from a template card** — orgs often require
   extra fields (job codes, KPI categories) whose option IDs nobody remembers.
   Don't ask — auto-pick the user's most recent **Done** card in the project
   (or one they name), `getJiraIssue` it, and copy:
   - `teamValue` ← the team field's id (bare UUID string)
   - `createDefaults` ← priority + each required custom field, as `{"id": ...}`
   - `epicParent` ← its parent's key if it hangs under an epic, else `null`
7. **Transitions** — `getTransitionsForJiraIssue` on that same card. Map by
   name to `transitions.toDo / inProgress / done`. Different status names →
   map by category (new → toDo, indeterminate → inProgress, done → done) and
   note the mapping in the summary.
8. **Conventions** — start from `profile-example.md` (sprint naming
   `YY-MM{A|B} <suffix>`, SP 0–3 in 0.125 steps, Thai working calendar, natural
   Thai/English summary style). Derive `board.suffix` and `board.id` from the
   template card's sprint name/boardId. Don't interrogate the user about
   conventions — show the chosen values in the final summary.

## Known-instance fast-path

If the site matches an instance you've already profiled, the instance-level IDs
may already be known (`profile-example.md`) — seed them, but still run steps 5
and 7 to verify (another project can expose a different workflow). The
per-project parts — project, epic, board suffix, which job-code/category options
this work uses — always come from live discovery.

## Finish

Write the file, then show one compact table: each value + where it came from
(discovered / template card / profile default). If setup was triggered from
inside another mode, continue that mode immediately — same turn, no hand-off.

## Drift

A later "unknown field" or "invalid transition" error means an admin changed
something — re-run this discovery; it's idempotent.
