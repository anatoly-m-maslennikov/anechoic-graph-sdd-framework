---
identity:
  atom_id: CA-E-788
  ref_id: CA-E-788@6-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Storage <+ Temporary State
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 7
relations:
  evaluation_for:
  - CA-M-462
  - CA-M-463
  - CA-O-240
  - CA-C-701
  - CA-R-2729
  IS_REPLACEMENT_FOR:
  - CA-E-751
  - CA-E-788
state:
  status: draft
  version: 6
  updated_at: '2026-11-14T00:32:48.561052+00:00'
destination:
  file:
    name: CA-E-788@6-draft-WORKBENCH_BACKEND-EVAL_CASE--verify-cached-result-lifecycle.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Verify cached result lifecycle

## Claim

### Prose Claim

Verify cached result lifecycle with actual Workbench queries, Views, expiry,
and native DuckDB table inspection. Use actual runtime evidence.

## Details

- Query-result files serve delivery only. They carry no cache, restore, or pin state.
- Verify that the result lifecycle adds no settings writes, staging, or restore path.

### Admission and rerun

- Reject multi-statement SQL. Invalid structured Run or View requests leave
  the last result reachable.
- Editing SQL alone preserves the last result.
- An admitted View rerun releases the old result even when SQL fails.

### Retention

- Open Views pin results beyond TTL. Closing keeps young results reachable
  and allows old unpinned results to expire.
- Verify a one-second TTL after explicit restart.
- Restart clears result tables and IDs.

### Delivery failures

- First-page `NaN` or infinity conversion failure leaves no ID,
  registration, or table.
- Later-page conversion failure preserves the known ID for other fetches.
- Export failure returns the known ID and delivery error without a path
  and leaves valid later fetches possible.
- Partial files never count as complete.
