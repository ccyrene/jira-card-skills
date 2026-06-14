# jira-card-skills — repo instructions

This repo *is* the source for the `/jira-card` Claude Code skill. You are likely
editing the skill, not using it.

- `skills/jira-card/SKILL.md` is a short router; each mode's procedure lives in
  `skills/jira-card/reference/`. Keep the router short — push detail into the
  reference files.
- Keep `SKILL.md`'s routing table, `README.md`, and
  `.claude-plugin/plugin.json` in sync when modes change (see
  `CONTRIBUTING.md`).
- After editing, run `./scripts/link-skills.sh` to refresh the symlink in
  `~/.claude/skills`.
- Architectural rule: setup discovers instance IDs into a per-target-repo
  `.claude/jira-config.json`; the workflow modes only read that file. No
  hardcoded cloudIds, custom-field numbers, or transition ids in procedures.
- UX rule: no prerequisite commands, at most one question in setup, one
  confirmation gate before writes, explicit approval before Done. Create mode
  may ask one batched round of clarifying questions when a card's details are
  unclear — the single allowed exception, and it comes before (not instead of)
  the gate.
- Instance facts (verified field IDs, required custom-field options,
  transitions, calendar) are in `skills/jira-card/reference/profile-example.md`.
- `archive/` is the pre-generalization original; never link or register it.
