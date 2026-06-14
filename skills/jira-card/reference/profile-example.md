# Example instance profile

Instance-level facts for `your-org.atlassian.net`, verified live against
project `PROJ` (Task issue type `10071`). These are **shared across the whole
instance** — every colleague's config reuses the same field IDs, transitions,
and team UUID. What differs per person/project: the **project key, epic parent,
board suffix, assignee**, and which **option values** their work uses (job code
/ group). Always re-verify fields and transitions per `setup.md` steps 5/7 — a
project could expose a different workflow.

## Instance coordinates

| Thing | Value |
|---|---|
| Site | `https://your-org.atlassian.net` |
| cloudId | `00000000-0000-0000-0000-000000000000` |
| Team field | `customfield_10001` (`atlassian-team`) — TEAM = `00000000-0000-0000-0000-000000000000` |
| Story Points | `customfield_10016` (float) |
| Sprint | `customfield_10020` (`gh-sprint`) |
| Job Code | `customfield_XXXXX` (cascading select) |
| Category | `customfield_XXXXX` (select) |
| Group | `customfield_XXXXX` (select) |

## Transitions (PROJ standard workflow)

| Transition | id | → status |
|---|---|---|
| To Do | `11` | To Do (`10070`) |
| In Progress | `21` | In Progress (`3`) |
| Done | `31` | Done (`10071`) |

## PROJ / TEAM project specifics (an example config)

- Project `PROJ` id `10000` — "Example Project"
- Board id `1`, sprint suffix `TEAM`, sprint naming `YY-MM{A|B} TEAM`
- Epic parent `PROJ-1` — "Example Epic"
- Template card mirrored for defaults: `PROJ-123`

## Common option values (set the parent id; child optional)

**Job Code (`customfield_XXXXX`)** — pass `{"id": "<parent>"}`:

| id | value |
|---|---|
| `10001` | Option A |
| `10002` | Option B |
| `10003` | Option C |

(Each may have children, e.g. Option A → `10010` "Option A child". Example cards
use the parent `Option A` alone, which Jira accepts.)

**Category (`customfield_XXXXX`)** — `{"id": "<id>"}`:

| id | value |
|---|---|
| `10011` | Option A |
| `10012` | Option B |
| `10013` | Option C |

**Group (`customfield_XXXXX`)** — `{"id": "<id>"}`:

| id | value |
|---|---|
| `10021` | Option A |
| `10022` | Option B |
| `10023` | Option C |

Example cards mirror `PROJ-123`: Job Code `Option A` (`10001`), Category
`Option B` (`10012`), Group `Option A` (`10021`), Team `TEAM`, priority `Medium`.

## Calendar notes (confirmed)
- Skip Sat–Sun.
- **5/1 Labour Day → WORK** (in `workingHolidays`).
- **5/4 Coronation Day → OFF** (in `holidays`).
- Other public holidays: ask per occurrence; do not assume any default calendar.
