---
identity:
  atom_id: CA-E-750
  ref_id: CA-E-750@5-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Source Retrieval
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
  tier: 6
relations:
  evaluation_for:
  - CA-C-700
  - CA-M-465
  - CA-R-2725
  IS_REPLACEMENT_FOR:
  - CA-E-750
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T23:58:37.308818+00:00'
destination:
  file:
    name: CA-E-750@5-draft-WORKBENCH_BACKEND-EVAL_CASE--verify-role-only-draft-reference-identity.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Verify role-only Draft reference identity.

## Claim

### Prose Claim

Verify that role-only Draft carriers with the same Atom ID remain distinct.

## Details

### Shared Atom ID

- Keep every carrier.
- Keep the Atom ID unchanged.
- Give each carrier a unique technical reference using the role-only ID
  and Project-relative carrier path.

### Coverage

- Verify six `CA-O-draft` lifecycle carriers under distinct paths.
- Verify that numbered Draft and Current canonical references stay unchanged.
