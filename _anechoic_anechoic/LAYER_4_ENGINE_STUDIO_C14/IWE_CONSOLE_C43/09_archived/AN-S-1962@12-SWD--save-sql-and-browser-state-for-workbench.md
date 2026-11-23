---
atom_family: SPEC
atom_id: AN-S-1962
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 12
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Save SQL and browser state for Workbench

## Claim scope

Open SQL Tabs, browser drafts and saved-item Journal records.

## Claim

### Prose Claim

Persist each open Tab query, local name and tabs in browser localStorage every five seconds and restore on load; ask before unsaved close, flush on pagehide/beforeunload when possible. Persist density with Theme/text/interface zoom/workspace settings: Compact default only explicit embedded, Comfortable standalone, saved preference wins; do not infer embedding from screen/Workspace.

Neither ordinary Run nor Check creates a permanent saved item. Run & Save executes the exact submitted SQL and then synchronously writes that same SQL and an optional creation name; for a selected Run it saves only the selected SQL, while Save Tab snapshots the full Tab script; failure writes nothing, while a post-Run save failure keeps result/ID/prior saved identity/dirty state, shows an error and neither retries nor rolls back. After Run and requested synchronous Save handling, automatic Run history is submitted asynchronously under CA-M-534; Check is not logged. Save snapshots the full Tab script. Unfinished editing is allowed; Run or Check uses the whole script or explicit statement selection under CA-R-2728.

Browser drafts remain separate from the Project Journal; saved links stay in the current Workbench context. The existing date-partitioned writer avoids Atom reindexing. Use Python 3.14 `uuid.uuid7()` only; historical worksheet/q_/w_ sources remain read-only. Reload reuses an open Tab by exact saved ID—not equal SQL—without losing edits or results. Duplicate after sync copies query and cursor only into an independent unsaved/no-result Tab with the first unused `(n)` suffix. Automatic Run history remains asynchronous and distinct from saved items.
