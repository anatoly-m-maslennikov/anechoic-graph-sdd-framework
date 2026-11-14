---
identity:
  atom_id: CA-E-752
  ref_id: CA-E-752@5-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Execution Control <+ Failure Handling
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
  tier: 6
relations:
  evaluation_for:
  - CA-C-702
  - CA-M-462
  - CA-M-396
  IS_REPLACEMENT_FOR:
  - CA-E-752
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T23:56:14.732491+00:00'
destination:
  file:
    name: CA-E-752@5-draft-WORKBENCH_BACKEND-EVAL_CASE--verify-query-failure-severity-and-runtime-availability.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Verify query-failure severity and runtime availability.

## Claim

### Prose Claim

Verify that Workbench reports query and runtime failures at the right severity
and keeps a healthy owner usable after a rejected request.

## Details

### Invalid SQL or query arguments

- Return a useful request error.
- Log `query_error` at WARNING.
- Return `outcome: failed`.
- Verify that a valid native MCP/HTTP request succeeds after an invalid one.

### Runtime failures

When Workbench is unavailable or the runtime fails unexpectedly:

- Log at ERROR.
- Return `outcome: blocked`.
- Keep the restart/runtime boundary.
