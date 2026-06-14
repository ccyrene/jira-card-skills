# Contributing

## Mental model

One skill, two layers:

- **`skills/jira-card/SKILL.md`** is a short router — intent table, the config
  rule, the guardrails. Keep it under ~60 lines; it loads on every invocation.
- **`skills/jira-card/reference/*.md`** hold each command's full procedure
  (create, backfill, implement, browse, setup, list) plus the config schema and
  the example instance profile. These load only when their command runs. Command
  words are always lowercase.

The other seam: setup discovers a project's instance-specific IDs and freezes
them into `<target-repo>/.claude/jira-config.json`; the workflow modes only read
that file. **Never hardcode a cloudId, `customfield_NNNNN`, or transition id in
a mode procedure** — add it to the config schema and discover it in setup.

## UX rules (the reason the skill was restructured — keep them)

- Zero prerequisite commands: a missing config triggers inline discovery, then
  the original request continues in the same turn.
- One confirmation gate before cards are written, and the
  Done-needs-explicit-approval gate in implement mode. Setup asks at most one
  question (usually none). The one sanctioned extra prompt is Create mode's
  batched clarifying round, asked only when a card can't be written well from
  what's given — everywhere else, fold information into a gate instead of adding
  questions.

## Making changes

- **New mode** → add `reference/<mode>.md`, add a row to the routing table in
  `SKILL.md`, mention it in `README.md`.
- **Config schema change** → update `reference/config-schema.md` (the contract)
  and `config.example.json` (a valid instance) together, then the consuming
  procedures. Bump `version` in `.claude-plugin/plugin.json`.
- **Conventions are data, not code** — sprint naming, calendar, SP rules, and
  summary style live under `conventions` in each repo's config. Ship defaults
  (the example profile), never bake a team's calendar into a procedure.

## Testing

Run `/jira-card` in a real repo: once with no config (exercises inline setup),
then each mode up to its gate — create stops at the draft card, backfill stops
at the draft table, implement stops at card pick / diff approval — and check the
drafts. The gates mean nothing is written to Jira during a dry run.
