---
identity:
  atom_id: CA-E-782
  ref_id: CA-E-782@5-draft
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
  - CA-R-2727
  - CA-D-674
  IS_REPLACEMENT_FOR:
  - CA-E-782
state:
  status: draft
  version: 5
  updated_at: '2026-11-14T07:53:31.737631+00:00'
destination:
  file:
    name: CA-E-782@5-draft-WORKBENCH_FRONTEND-EVAL_CASE--verify-the-shared-view-rename-modal.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-46_FEATURE_WORKBENCH_FRONTEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_FRONTEND
claim_target_scope_unit: WORKBENCH_FRONTEND
author: Anatoly Maslennikov
---
## Summary

Verify the shared View rename modal

## Claim

### Prose Claim

Verify that double-clicking a View name or choosing Rename View in the palette
opens the same modal with the displayed name prefilled.

## Details

- Confirm renames the View and survives refresh or reload.
- Cancel, Escape, single clicks, and unrelated query or autosave leave
  the name unchanged.
