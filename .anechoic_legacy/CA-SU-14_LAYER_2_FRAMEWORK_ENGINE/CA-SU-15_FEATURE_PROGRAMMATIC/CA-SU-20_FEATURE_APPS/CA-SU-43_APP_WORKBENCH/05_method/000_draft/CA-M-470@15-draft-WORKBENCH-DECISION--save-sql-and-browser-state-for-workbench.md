---
identity:
  atom_id: CA-M-470
  ref_id: CA-M-470@15-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Method
  form: Decision
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Storage
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 4
relations:
  method_for:
  - CA-R-2727
  - CA-R-2729
  - CA-R-2776
  IS_REPLACEMENT_FOR:
  - CA-M-470
state:
  status: draft
  version: 15
  updated_at: '2026-11-13T20:51:24.299842+00:00'
destination:
  file:
    name: CA-M-470@15-draft-WORKBENCH-DECISION--save-sql-and-browser-state-for-workbench.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/05_method/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
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
