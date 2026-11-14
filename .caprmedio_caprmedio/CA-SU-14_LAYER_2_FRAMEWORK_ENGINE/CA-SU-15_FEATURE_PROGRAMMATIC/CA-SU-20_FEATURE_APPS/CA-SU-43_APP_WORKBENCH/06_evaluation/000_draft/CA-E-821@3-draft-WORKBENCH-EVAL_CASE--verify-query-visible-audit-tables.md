---
identity:
  atom_id: CA-E-821
  ref_id: CA-E-821@3-draft
context:
  container:
    scope_unit: CA-SU-43
  role: evaluation
  form: Eval Case
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Projection
  tier: 6
relations:
  evaluation_for:
  - CA-R-3066
  - CA-R-3067
  - CA-R-3068
  - CA-M-549
  - CA-D-715
  IS_REPLACEMENT_FOR:
  - CA-E-821
state:
  status: draft
  version: 3
  updated_at: '2026-11-14T07:53:38.798834+00:00'
destination:
  file:
    name: CA-E-821@3-draft-WORKBENCH-EVAL_CASE--verify-query-visible-audit-tables.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/06_evaluation/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
---
## Summary

Verify query-visible audit tables

## Claim

### Prose Claim

Verify archive selection and query-visible diagnostics through the real
Workbench backend.

## Details

- Cold start exposes Current, Draft, and Backlog. Load two Archive Scope Unit
  and Role pairs. Verify scoped coverage and repeat loading without duplicates.
- Distinguish unloaded history from absent revisions. ID and Version allocation
  accounts for unloaded Archives. Lifecycle can read a newly archived exact file.
- Verify all five issue types from CA-D-715. Parseable files stay queryable,
  Draft and Backlog stay out of duplicate checks, and source bytes are preserved.
- Delayed audits leave committed rows and lifecycle responses available.
  Verify elapsed time, latest diagnostics, and HTTP/MCP parity.
