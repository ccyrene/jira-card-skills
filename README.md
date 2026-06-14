# jira-card-skills

One [Claude Code](https://claude.com/claude-code) skill — **`/jira-card`** — for
the whole Jira card loop, right from your terminal.

The common case is dead simple: **describe a task in one sentence and it creates
a well-formed card.**

```text
/jira-card "harden the service against an API timeout, due Friday, 2pt, priority high"
```

It figures out the board and project first, then reads the sprint, due date,
story points and priority from your words plus the repo config — asking only
when something is genuinely unclear — shows you one draft to confirm, and writes
the card (left as **To Do**).

## What it can do

The same command routes by what you ask. All command words are lowercase:

| You say | What happens |
| --- | --- |
| `/jira-card "<description>"` | **create** one well-formed card from a sentence |
| `/jira-card backfill` | **backfill** cards from your git commit history |
| `/jira-card implement KEY` | **implement** — pick up a backlog card and build it |
| `/jira-card browse` | **browse** — list candidate To-Do cards |
| `/jira-card setup` | **setup** — (re)discover the project config |
| `/jira-card list` | **list** — show every command and its options |

No separate setup step is required. If a repo has no config yet, the skill
discovers it inline (asking at most "which project?") and continues with what
you asked.

## Config-driven, no hardcoded IDs

Nothing about your Jira instance is baked into the skill. The first run in a
repo auto-discovers everything it needs — custom-field numbers, transition IDs,
team, board and epic, *by name* — through the Atlassian MCP, and freezes it into
a per-repo config at `<repo-root>/.claude/jira-config.json`. The same skill then
works on any project and any workflow; different repos map to different
projects. The config holds project-level facts only (no secrets), so a committed
file works for the whole team.

## Install

You need Claude Code with the **Atlassian MCP**. Don't have it connected yet?
`/jira-card` offers to register it on the first run — you just do the one-time
`/mcp` → Atlassian **Authenticate** step and re-run.

```bash
git clone https://github.com/ccyrene/jira-card-skills.git
cd jira-card-skills
./scripts/link-skills.sh        # symlinks the skill into ~/.claude/skills
```

That's it. Open Claude Code in any repo and type `/jira-card`.

## Guardrails

- **Exactly one confirmation** before any card is written.
- A card is **never** moved to **Done** without your explicit approval.
- Your code is **never** auto-committed.

## Learn more

- Skill router: [`skills/jira-card/SKILL.md`](./skills/jira-card/SKILL.md)
- Per-command procedures: [`skills/jira-card/reference/`](./skills/jira-card/reference/)
- Config schema: [`skills/jira-card/reference/config-schema.md`](./skills/jira-card/reference/config-schema.md)
- Example profile: [`skills/jira-card/reference/profile-example.md`](./skills/jira-card/reference/profile-example.md)
