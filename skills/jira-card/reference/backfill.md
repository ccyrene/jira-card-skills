# Backfill — cards from git commits

Commits have outrun the board. Cluster them into cards, make sure every working
day is covered, create everything in one approved batch, and close the cards as
Done — the work already shipped.

Steps 1–4 are planning (no Jira writes). Step 5 is the single confirmation.
Step 6 submits everything.

## 1. Find the boundary

Newest card by the user in this project:
```jql
project = <project.key> AND (assignee = currentUser() OR reporter = currentUser())
ORDER BY updated DESC
```
Its date is the boundary — work after it needs cards. Note its sprint.

## 2. Collect commits

```bash
git log --since="<boundary-date>" --pretty=format:"%h %ad %s" --date=short
```
Commits batch-pushed on a non-working day (e.g. Sunday): read the subjects and
`git show --stat` to assign the work to the real working days before it.

## 3. Working-day grid — the no-gap check

This is the step that gets skipped when rushing. Don't.

List every working day in the sprint window using `conventions.calendar`:
keep only `workdays` weekdays, drop dates in `holidays`, keep dates in
`workingHolidays` (public holiday, but this team works it). For each day, note
which commit (or known non-code work) covers it. Days with nothing get a
**"no work found — ?"** row in the draft — never invent a card to fill a gap;
the user resolves those at the gate.

## 4. Cluster and estimate

- 1 card ≈ 1 coherent topic (a feature, a security pass, a pipeline).
- SP = focused hours ÷ `storyPoints.hoursPerDay`, rounded to
  `storyPoints.granularity`, never above `storyPoints.max` — split bigger
  topics into more cards.
- Due date = the last working day the cluster spans (a weekend push → the
  Friday before).
- Summaries follow `conventions.summaryStyle`. Vary the lead verb across the
  batch; write final-quality wording on the first draft.

## 5. The one gate

Show, in a single message: the working-day grid (including any "?" days) and
the card table — Summary, SP, Due, Sprint. The user fixes wording or fills
gaps in their reply. On an explicit go ("post เลย", "submit", "go") proceed to
step 6 with **no further questions**.

## 6. Submit — three calls per card

`createJiraIssue` can't set Team and can't reliably set Sprint, hence the
sequence:

**a. Create** — `createJiraIssue`:
```json
{
  "cloudId": "<cloudId>",
  "projectKey": "<project.key>",
  "issueTypeName": "<issueType.name>",
  "parent": "<epicParent>",            // omit if null
  "assignee_account_id": "<current user's accountId>",
  "summary": "<summary>",
  "additional_fields": {
    "<fields.dueDate>": "YYYY-MM-DD",
    "<fields.storyPoints>": <sp>,
    // ...plus every key/value from createDefaults
  }
}
```

**b. Sprint + Team** — `editJiraIssue`. Sprint id: render the sprint name from
the due date via `conventions.sprintNaming`, JQL `sprint = "<name>"`, read
`<fields.sprint>[0].id` off any hit.
```json
{ "fields": {
    "<fields.sprint>": <sprint-id-number>,
    "<fields.team>": "<teamValue>"     // bare UUID string; skip if null
} }
```

**c. Done** — `transitionJiraIssue` with `<transitions.done>`.

Creates of different cards may run in parallel; a card's b/c must follow its
own a.

## Pitfalls

- Team rejected at create time is **expected** — that's why it's set in (b).
- A commit on day 16 of the month belongs to the second-half sprint, not the
  first — check due dates against the sprint split.
- Never let a card exceed `storyPoints.max`; split it.

## Finish

One table — Key, Summary, SP, Due, Sprint, Status — with
`<site>/browse/<KEY>` links. Offer the natural next step (start the next
half-sprint, or pick up a backlog card).
