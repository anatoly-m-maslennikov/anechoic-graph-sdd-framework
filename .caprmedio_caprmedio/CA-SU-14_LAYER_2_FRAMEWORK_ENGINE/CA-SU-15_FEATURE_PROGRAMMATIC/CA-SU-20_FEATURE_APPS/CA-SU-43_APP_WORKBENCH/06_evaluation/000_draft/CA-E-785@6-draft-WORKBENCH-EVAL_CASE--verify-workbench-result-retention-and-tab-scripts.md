---
identity:
  atom_id: CA-E-785
  ref_id: CA-E-785@6-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Storage <+ Temporary State
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-R-2776
  - CA-M-470
  - CA-D-675
  IS_REPLACEMENT_FOR:
  - CA-E-785
state:
  status: draft
  version: 6
  updated_at: '2026-11-14T00:32:45.296333+00:00'
destination:
  file:
    name: CA-E-785@6-draft-WORKBENCH-EVAL_CASE--verify-workbench-result-retention-and-tab-scripts.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/06_evaluation/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
---
## Summary

Verify Workbench result retention and Tab scripts

## Claim

### Prose Claim

Verify shared Workbench result retention and Tab SQL through real MCP and
browser interfaces.

## Details

- Settings edits alone change neither source files nor the watcher log.

### Startup settings

- A missing settings file gives a TTL of 3,600 seconds.
- A valid TTL of one second takes effect only after restart or reread.
- A TTL of zero fails through stderr. Verify there is no default fallback.
- Verify the runtime settings file is outside the watcher root.

### Shared result cache

- Run through one interface and inspect or page through the other.
  Verify both surfaces agree.
- Record creation time with a monotonic clock.
- Before TTL, an unpinned result is available. After TTL, idle, Run, or Page
  cleanup may expire it.
- An open View pins a result beyond TTL. Closing unpins it.
  A young result stays available and an old one may expire.
- Verify retention needs no heartbeat, lease, crash recovery, scheduler, or service.
- Rerun drops the prior result before replacement. A failed replacement leaves
  the prior ID unavailable.
- Restart clears transient tables and IDs and rebuilds the Projection.
  Saved queries and the View Journal survive.

### Tab SQL

- Unfinished SQL is editable. Run and Check accept one complete query and
  reject multiple statements under CA-R-2728.
- Run & Save stores the exact submitted SQL. Save View stores the full Tab SQL.
