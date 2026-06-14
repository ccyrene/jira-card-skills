# Implement — pick up a card, build it, move it across the board

Two user interactions in the whole flow: **pick the card** (that's the start
signal) and **approve the diff** (that's the finish signal). Everything in
between runs without asking.

## 1. Find candidates

Current sprint first; backlog as fallback. Cap at ~10. Add
`AND parent = <epicParent>` when the config sets one.

```jql
project = <project.key> AND status = "To Do"
  AND (sprint in openSprints() OR sprint in futureSprints())
ORDER BY duedate ASC, created DESC

project = <project.key> AND status = "To Do" AND sprint is EMPTY
ORDER BY created DESC
```

`futureSprints()` is not optional: many boards assign cards to a sprint at
planning but never click "start sprint", so the current sprint sits in state
`future` forever and `openSprints()` alone returns nothing.

## 2. Present + pick

Numbered list: key, summary, sprint (or "backlog"), age. Make clear that
picking one **starts the work**. Accept a number, an issue key, a description
("the monitoring one"), or "skip".

**Browse mode ends here** — if the user only asked to see the backlog, show the
list and stop.

## 3. Establish scope (no extra questions)

`getJiraIssue` with `description, comment, parent, issuelinks, labels`.
If the description is empty (it often is), recover scope in this order:
`scope.featureDocs` entry matching the summary → `scope.todoList` → the repo's
own docs / knowledge graph / project skill. Open with a one-paragraph statement
of what you're about to build — as a heads-up, not a question.

## 4. In Progress — before any code

`transitionJiraIssue` with `<transitions.inProgress>`. This is what makes the
work visible to the team; forgetting it is the classic silent failure.

## 5. Build

- Mirror the repo's existing structure and style — read neighbouring modules
  first; load the project's own skill if it ships one.
- Run the nearest relevant tests.
- Show `git diff --stat` plus the key hunks — not whole files.
- **Never auto-commit.** The user stages and commits themselves.

## 6. Approval — the gate that stays

Wait for an explicit "ok / approve / ดูดี / merge ได้". Green tests are not
approval; neither is a vague acknowledgement. Feedback → iterate step 5.

## 7. Done + breadcrumb

`transitionJiraIssue` with `<transitions.done>`. After the user lands the
commit, optionally comment on the card (`addCommentToJiraIssue`):

```
implemented in <sha1>, <sha2> — <one-line summary>
```

so the ticket links back to the change.

## Pitfalls

- Coding while the card still says To Do — always step 4 first.
- Auto-Done without explicit approval — never.
- Treating an empty description as "no scope" — check `scope.*` sources first.

## Finish

Card's final status with its `<site>/browse/<KEY>` link, files changed, and the
next step (commit, another card, or stop).
