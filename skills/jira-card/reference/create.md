# Create — one card from a description (default mode)

The user describes work; turn it into one well-formed card. No commits required —
that's Backfill. Created cards stay **To Do** (creating ≠ shipping).

Flow: **board first → fill, ask anything unsure via the chat UI → full draft →
one go → create → remember the config for this repo/folder.**

## 1. Board / project FIRST — before any other field

Decide which **board (and its project)** the card goes on *before* touching
anything else. The board fixes the project, the sprint pool, the required fields,
and the defaults. **Do not assume the config's project.**

- User named one ("on TEAM board", "PROJ", "TEAM board") → resolve it:
  `getVisibleJiraProjects` (searchString) for the project, and read a recent
  card's `<fields.sprint>[].boardId`/name to confirm the board. If the named board
  is a **different project** than the config's, target the named one.
- Named board won't resolve, nothing named with >1 known board, or any doubt →
  **ask first** (structured UI, board picker). This is the first question.
- Nothing named and the repo/folder config has exactly one board → use it (still
  shown in the draft so the user can redirect).

⚠️ A short code like "TEAM" can be both a **Team value** *and* a **separate project**
(`TEAM`, board 1) — the user almost always means the board/project, not just the
Team field. Getting this wrong puts the card on the wrong board (see Pitfalls).

## 2. Parse the rest of the request

Pull the work + any inline NL hints (no flags):
- **summary** — rewrite to `conventions.summaryStyle` (don't echo verbatim).
- **due date** — "ศุกร์นี้"/"อีก 3 วันทำการ"/"15 ก.ค." → ISO via `conventions.calendar`.
- **story points** — "2pt"/"ครึ่งวัน" → SP via `storyPoints` rules.
- **sprint** — "sprint นี้"/none → the chosen board's active sprint; "sprint หน้า" → its next future sprint; named → that.
- **priority / parent / team** — only if stated; else the defaults below.

## 3. Resolve + clarify — ask anything unsure via the structured UI

Fill every field from the defaults table. For **anything still uncertain, ask the
user** with the **structured question UI** (`AskUserQuestion` — clickable options +
free-text "Other"): one prompt, each open item its own question, recommended
option first. **Ask for everything that's unclear** — don't guess on:

- which board/project (step 1), an unresolved sprint/date, an ambiguous priority;
- a **required** field on this project with no known default (e.g. Job Code /
  Category fields on a project we haven't configured before);
- a parent/epic when the board expects one and none is known.

Ask only about **card content the user decides** — never about internal mechanics
(missing config, which repo, MCP setup); resolve those silently. If nothing is
unsure, go straight to the draft.

### Defaults (apply silently; every one still appears in the draft)

| Field | Default |
|---|---|
| Reporter | currentUser (you) |
| Assignee | currentUser (you) |
| Sprint | the chosen board's **current/active** sprint |
| Story Points | **`conventions.storyPoints.default`** (e.g. `1`) |
| Priority | Medium |
| Team | config `teamValue` for that project (e.g. TEAM) |
| Job Code (`customfield_XXXXX`) · Category (`customfield_XXXXX`) · Group (`customfield_XXXXX`) | config `createDefaults` for that project; **ask** if the project is new and they're required |
| Parent (epic) | config `epicParent`, else none |
| Due date | none unless stated |

## 4. The one gate — full draft, every row

Show one table with **all** rows and where each value came from:

```
📝 จะสร้างการ์ดนี้ — แก้แถวไหนบอกได้ก่อนยืนยัน
┌───────────────────────────┬───────────────────────────────────────────────┐
│ Project                   │ TEAM — Example Project                          │
│ Board                     │ 1 (TEAM board)                                  │
│ Summary                   │ <summary>                                       │
│ Status                    │ To Do                                           │
│ Reporter                  │ คุณ (currentUser)                                │
│ Assignee                  │ คุณ (currentUser)                                │
│ Parent (epic)             │ <epic> | —                                      │
│ Sprint                    │ 26-06A TEAM (6A, active)       ← default        │
│ Due date                  │ <YYYY-MM-DD> | —                                │
│ Story Points              │ 1                              ← default        │
│ Priority                  │ Medium                         ← default        │
│ Team                      │ TEAM                                            │
│ Job Code                  │ Option A                                        │
│ Category                  │ Option A                                        │
│ Group                     │ Option A                                        │
└───────────────────────────┴───────────────────────────────────────────────┘
```

The user edits any row in their reply. On an explicit go ("ok", "สร้างเลย", "go")
→ step 5, no further questions.

## 5. Submit — two calls, no transition

**a. Create** — `createJiraIssue`: `projectKey`, `issueTypeName`, `parent` (omit if
none), `assignee_account_id` (currentUser), `summary`, `description`, and
`additional_fields`:
```json
{
  "<fields.storyPoints>": <sp, default conventions.storyPoints.default>,
  "<fields.dueDate>": "YYYY-MM-DD",     // omit if no due date
  "priority": { "name": "Medium" },
  "customfield_XXXXX": { "id": "<Job Code>" },
  "customfield_XXXXX": { "id": "<Category>" },
  "customfield_XXXXX": { "id": "<Group>" }
}
```
Reporter is currentUser automatically — set it only if it must differ.

**b. Sprint + Team** — `editJiraIssue` (create-time rejects both):
```json
{ "fields": {
    "<fields.sprint>": <sprint-id-number>,   // the chosen board's sprint id
    "<fields.team>": "<teamValue>"           // bare UUID; skip if null
} }
```

**No transition** — the card stays To Do.

## 6. Remember the config — per repo / per folder (NEVER user scope)

Once the board/project/defaults are resolved, persist them so the next card in
this context doesn't re-ask:

- Write/update `<repo-root>/.claude/jira-config.json`. If a **subfolder** targets a
  different board/project, write a `.claude/jira-config.json` in that folder;
  resolve from cwd upward.
- **Never** store the config (or register the MCP server) at **user scope** — a
  global config makes different repos/folders collide (the cross-project mixup). One
  repo/folder → its own board, project, and defaults.
- A config may list more than one board if the same folder legitimately targets
  several; keep the board the user picks as that context's default.

## Pitfalls

- **Wrong board = wrong project.** "TEAM board" = project `TEAM` (board 1), not
  PROJ — resolve the board (step 1) before creating, or the card lands on the
  wrong project.
- Team/Sprint rejected at create time is expected — that's why they're in (b).
- Don't close the card as Done; don't exceed `storyPoints.max` (split instead).
- Don't globalize config to user scope.

## Finish — always return the clickable link

End by returning the created card's **clickable link** so the user can open and
verify it in Jira. Make it the last thing they see:

> ✅ สร้างแล้ว: **[`<KEY>`](<site>/browse/<KEY>)** — `<summary>` · `<board>` · `<sprint>`

(render as a real markdown link, not bare text). Then offer the next step —
another card, or pick this one up via `implement`.
