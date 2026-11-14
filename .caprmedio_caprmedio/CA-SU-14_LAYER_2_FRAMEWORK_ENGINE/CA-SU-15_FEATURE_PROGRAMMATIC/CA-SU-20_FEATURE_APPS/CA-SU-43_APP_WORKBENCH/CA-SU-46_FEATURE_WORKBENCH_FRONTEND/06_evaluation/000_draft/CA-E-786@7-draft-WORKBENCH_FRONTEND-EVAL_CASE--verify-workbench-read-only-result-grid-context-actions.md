---
identity:
  atom_id: CA-E-786
  ref_id: CA-E-786@7-draft
context:
  container:
    scope_unit: CA-SU-46
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-M-492
  - CA-D-674
  IS_REPLACEMENT_FOR:
  - CA-E-786
state:
  status: draft
  version: 7
  updated_at: '2026-11-14T07:53:35.535093+00:00'
destination:
  file:
    name: CA-E-786@7-draft-WORKBENCH_FRONTEND-EVAL_CASE--verify-workbench-read-only-result-grid-context-actions.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-46_FEATURE_WORKBENCH_FRONTEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_FRONTEND
claim_target_scope_unit: WORKBENCH_FRONTEND
author: Anatoly Maslennikov
---
## Summary

Verify Workbench read-only result-grid context actions

## Claim

### Prose Claim

Verify read-only result-grid actions in standalone and explicit embedded
Workspaces, using a View with one complete query.

## Details

- Verify the exact grid actions defined by CA-R-2953. Copy and Show full value
  use the complete data even in Limited display.
- Sort and filter across the existing result. Group by one column with
  global counts. Pages stay correct and SQL never reruns.
- Verify approved actions leave the View and result unchanged. Resize, zoom,
  and display preferences affect presentation only.
