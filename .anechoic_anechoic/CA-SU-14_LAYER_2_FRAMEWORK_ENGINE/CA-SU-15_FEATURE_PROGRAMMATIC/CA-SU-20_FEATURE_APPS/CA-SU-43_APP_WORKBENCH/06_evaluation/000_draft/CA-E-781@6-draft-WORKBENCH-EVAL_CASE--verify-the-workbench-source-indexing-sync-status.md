---
identity:
  atom_id: CA-E-781
  ref_id: CA-E-781@6-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ State Synchronization
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-R-2952
  IS_REPLACEMENT_FOR:
  - CA-E-781
state:
  status: draft
  version: 6
  updated_at: '2026-11-14T00:32:29.280634+00:00'
destination:
  file:
    name: CA-E-781@6-draft-WORKBENCH-EVAL_CASE--verify-the-workbench-source-indexing-sync-status.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/06_evaluation/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
---
## Summary

Verify the Workbench source indexing sync status

## Claim

### Prose Claim

Verify the Workbench source indexing sync status in the built browser with
the real backend and its existing HTTP polling.

## Details

- Check visible controls and responses during long indexing.
- Query execution and autosave leave sync status unchanged.
- Verify that polling never restarts Workbench automatically.

### Status text

- The small top-right text uses local time.
- Initial indexing or refresh shows Syncing with `syncing: true`.
- Before the first success, false and a null timestamp show Not synced yet.
- A successful commit or confirmation shows false and a new offset timestamp.
- Failure preserves the prior timestamp and error. Polling reports no success.

### Status interfaces

- Compare the Project API, legacy Workbench URL, and MCP for the same Project.
  Sync state, Archive coverage, and audit state must match.
- Reject a mismatched Project binding.
