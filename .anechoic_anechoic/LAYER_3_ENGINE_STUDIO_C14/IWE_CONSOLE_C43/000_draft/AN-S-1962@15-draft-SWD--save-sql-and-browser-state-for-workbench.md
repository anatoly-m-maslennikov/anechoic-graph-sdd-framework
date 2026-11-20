---
atom_family: SPEC
atom_id: AN-S-1962
structure:
  container:
    component: C43
  tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 15
  updated_at: '2026-11-13T20:51:24.299842+00:00'
---
## Summary

Save SQL and browser state for Workbench

## Claim scope

Open SQL Tabs, browser drafts and saved-item Journal records.

## Claim

### Prose Claim

When browser storage is available, persist each open Tab query, local name and tabs in browser localStorage every five seconds. Restore them on load. Ask before unsaved close and flush on pagehide or beforeunload when possible. If storage cannot be read or written, keep the current standalone Workspace identity and unsaved edits in memory for the page session. Show the Operator that reload or close may lose those edits.

Persist density with Theme, text, interface zoom and workspace settings. Compact is the default only when explicitly embedded; Comfortable is the standalone default. A saved preference wins. Do not infer embedding from screen or Workspace.

Neither ordinary Run nor Check creates a permanent saved item. Run & Save executes the exact submitted query, then synchronously writes the same SQL and an optional creation name. Failure writes nothing. A post-Run save failure keeps the result, ID, prior saved identity and dirty state; shows an error; and neither retries nor rolls back. After Run and requested synchronous Save handling, submit automatic Run history asynchronously under CA-M-534. Check is not logged. Save View snapshots the Tab's full SQL text. Unfinished editing is allowed. Run or Check validates the complete query under CA-R-2728.

Keep browser drafts separate from the Project Journal and saved links in the current Workbench context. The existing date-partitioned writer avoids Atom reindexing. Use Python 3.14 `uuid.uuid7()` only. Historical worksheet/q_/w_ sources remain read-only.

On reload, reuse an open Tab by exact saved ID, not equal SQL, without losing edits or results. Duplicate after sync copies query and cursor only into an independent unsaved Tab with no result and the first unused `(n)` suffix. Automatic Run history remains distinct from saved items.
