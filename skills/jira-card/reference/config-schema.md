# jira-config.json schema

The file setup mode (`setup.md`) writes and the workflow modes read. Lives **per
repo** at `<repo-root>/.claude/jira-config.json` — or **per folder** (resolved from
cwd upward) if a subfolder targets a different project. **Never a single
user-global config:** different repos/folders map to different Jira
projects/boards, and a shared one makes them collide. See `../config.example.json`
for a filled example instance.

All `customfield_NNNNN` numbers and transition IDs are **instance-specific** —
never copy them between Jira sites. Let setup mode discover them.

## Top-level keys

| Key | Type | Meaning |
|---|---|---|
| `site` | string | Jira site URL, e.g. `https://your-org.atlassian.net`. Used only for `browse/` links. |
| `cloudId` | string (UUID) | Passed as `cloudId` to every MCP call. |
| `project` | `{key, id, name}` | Target project. `key` (e.g. `PROJ`) is used in JQL; `id` is informational. |
| `board` | `{id, suffix}` | `id` = agile board id; `suffix` = the trailing token in sprint names (e.g. `TEAM`). |
| `epicParent` | string \| null | Issue key every created card links under as `parent` (e.g. `PROJ-1`). `null` = no epic. |
| `assignee` | string | `"currentUser"` sentinel → resolve live via `atlassianUserInfo` / JQL `currentUser()`. A literal accountId pins all cards to one person (not recommended for shared configs). |
| `issueType` | `{name, id}` | Work-item type cards are created as (usually `Task`). |
| `fields` | object | Map of role → field key. Required: `storyPoints`, `sprint`, `team`. Optional `dueDate` — usually the built-in `"duedate"`; Create and Backfill set it from natural-language dates via `conventions.calendar`. |
| `teamValue` | string (UUID) \| null | The Team option to set. Passed as a **bare UUID string** in an `editJiraIssue` follow-up (create-time rejects it). |
| `createDefaults` | object | Fields stamped on every created card at create time. Keys are real field ids (`priority`, `customfield_*`); values match Jira's set-shape (`{name}` for priority, `{id}` for select/cascading). |
| `transitions` | `{toDo, inProgress, done}` | Transition **ids** (strings) for this project's workflow. |
| `conventions` | object | Human conventions — see below. |
| `scope` | object | Optional pointers to in-repo scope docs the implement flow reads. |

## `conventions`

| Key | Meaning |
|---|---|
| `sprintNaming` | Pattern string, e.g. `"YY-MM{A|B} TEAM"`. `A` = days 1–15, `B` = 16–end-of-month. The skills render a name from a due date, then resolve its live sprint **id** via JQL `sprint = "<name>"` (ids are not predictable). |
| `storyPoints` | `{min, max, granularity, hoursPerDay, default}`. Per-card SP must satisfy `min ≤ sp ≤ max` and be a multiple of `granularity`. `hoursPerDay` maps effort→SP (`1 day = hoursPerDay h = 1 SP`). `default` is used when the user gives no estimate (Create stamps it). Example: `0 < sp ≤ 3`, step `0.125` (1h), 8h/day, `default` `1`. Split work that exceeds `max` into multiple cards. |
| `calendar.workdays` | Weekday short-names that count as working days. |
| `calendar.holidays` | Explicit `YYYY-MM-DD` off-days (no card due here). |
| `calendar.workingHolidays` | Explicit `YYYY-MM-DD` that are public holidays but the team **still works** (e.g. some teams work Labour Day, 5/1). |
| `calendar.askWhenUnsure` | If true, never assume a national holiday calendar — ask the user about any date in doubt. |
| `summaryStyle` | Prose guidance for card summaries. Read it verbatim before drafting. |

## `scope` (optional)

| Key | Meaning |
|---|---|
| `featureDocs` | Repo-relative path to a feature/spec doc the implement flow consults for card scope when a card description is empty. Omit if none. |
| `todoList` | Repo-relative path to a top-level TODO/backlog doc. Omit if none. |

Unknown/omitted optional keys are fine — the skills degrade gracefully (skip the
scope lookup, treat `epicParent:null` as "no parent", etc.).
