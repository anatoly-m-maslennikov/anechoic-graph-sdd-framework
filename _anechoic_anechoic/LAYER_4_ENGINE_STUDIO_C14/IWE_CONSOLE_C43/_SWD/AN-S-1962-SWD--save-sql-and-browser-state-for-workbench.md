---
atom_family: SPEC
atom_id: AN-S-1962
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 14
  updated_at: '2026-11-12T16:57:52.021857+00:00'
---
## Summary

Save SQL and browser state for Workbench

## Claim scope

Open SQL Tabs, browser drafts and saved-item Journal records.

## Claim

### Prose Claim

When browser storage is available, persist each open Tab query, local name and tabs in browser localStorage every five seconds and restore on load; ask before unsaved close, flush on pagehide/beforeunload when possible. If storage cannot be read or written, keep the current standalone Workspace identity and unsaved edits in memory for the page session. Show the Operator that reload or close may lose those edits. Persist density with Theme/text/interface zoom/workspace settings: Compact default only explicit embedded, Comfortable standalone, saved preference wins; do not infer embedding from screen/Workspace.

Neither ordinary Run nor Check creates a permanent saved item. Run & Save executes the exact submitted query and then synchronously writes the same SQL and an optional creation name; failure writes nothing, while a post-Run save failure keeps result/ID/prior saved identity/dirty state, shows an error and neither retries nor rolls back. After Run and requested synchronous Save handling, automatic Run history is submitted asynchronously under CA-M-534; Check is not logged. Save View snapshots the Tab's full SQL text. Unfinished editing is allowed. Run or Check validates the complete query under CA-R-2728.

Browser drafts remain separate from the Project Journal; saved links stay in the current Workbench context. The existing date-partitioned writer avoids Atom reindexing. Use Python 3.14 `uuid.uuid7()` only; historical worksheet/q_/w_ sources remain read-only. Reload reuses an open Tab by exact saved ID—not equal SQL—without losing edits or results. Duplicate after sync copies query and cursor only into an independent unsaved/no-result Tab with the first unused `(n)` suffix. Automatic Run history remains asynchronous and distinct from saved items.
