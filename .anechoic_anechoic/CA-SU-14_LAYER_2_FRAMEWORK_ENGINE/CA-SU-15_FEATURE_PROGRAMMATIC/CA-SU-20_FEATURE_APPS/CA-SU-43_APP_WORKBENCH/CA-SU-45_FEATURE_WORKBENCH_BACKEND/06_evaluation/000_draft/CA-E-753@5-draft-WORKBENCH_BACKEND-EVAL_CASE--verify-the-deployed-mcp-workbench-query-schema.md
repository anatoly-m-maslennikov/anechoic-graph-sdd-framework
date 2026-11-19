---
identity:
  atom_id: CA-E-753
  ref_id: CA-E-753@5-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development
      <+ Architecture <+ Communication <+ Interface Contracts
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 6
relations:
  evaluation_for:
  - CA-C-703
  - CA-R-2728
  - CA-M-462
  - CA-D-673
  IS_REPLACEMENT_FOR:
  - CA-E-753
state:
  status: draft
  version: 5
  updated_at: '2026-11-14T07:52:57.241838+00:00'
destination:
  file:
    name: CA-E-753@5-draft-WORKBENCH_BACKEND-EVAL_CASE--verify-the-deployed-mcp-workbench-query-schema.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Verify the deployed MCP Workbench query schema.

## Claim

### Prose Claim

Verify that deployed MCP requires `sql` and accepts a non-negative integer
`preview` and boolean `save` as optional arguments.

Use a native SDK call with `preview: 0` and `save: false`. It returns zero
preview rows, creates no saved query, and preserves the shared contract.
