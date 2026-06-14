# list — show every /jira-card command and its params

`/jira-card list` (also "help", "มีคำสั่งอะไรบ้าง") prints the usage below and
stops — it touches no card. **Every command word is lowercase.**

## Commands

| Command | What it does |
|---|---|
| `/jira-card "<desc>"` | **create** (default) — one card from a description. Resolves the board first, asks anything unclear via the choice UI, shows a full draft, then creates it as To Do. |
| `/jira-card create "<desc>"` | same as above, written explicitly. |
| `/jira-card backfill` | cards from git commits, closed as Done (work already shipped). |
| `/jira-card implement <key>` | pick a To-Do card, build it, move it across the board (Done only on your approval). |
| `/jira-card browse` | list candidate To-Do cards and stop. |
| `/jira-card setup` | (re)discover this repo/folder's project config. |
| `/jira-card list` | this help. |

## create params (plain words inside the description — no flags, all lowercase)

| Param | Meaning | Default |
|---|---|---|
| `board` | which board/project the card lands on — resolved first | asked if unclear |
| `summary` | the work itself | from your text |
| `sprint` | "sprint นี้" / "sprint หน้า" / a sprint name | the board's current sprint |
| `due` | "ศุกร์นี้", "อีก 3 วันทำการ", "15 ก.ค." | none |
| `points` | "2pt", "ครึ่งวัน" | 1 |
| `priority` | "ด่วน" / "high" / "low" | medium |
| `parent` | epic key | config epic, else none |
| `team` | team value | config team |
| `reporter` | who reports it | you |
| `assignee` | who it's assigned to | you |
| `job code` | job code | config default |
| `category` | appraisal category | config default |
| `group` | individual group | config default |

Anything unclear → the skill asks via the structured choice UI before the draft.
