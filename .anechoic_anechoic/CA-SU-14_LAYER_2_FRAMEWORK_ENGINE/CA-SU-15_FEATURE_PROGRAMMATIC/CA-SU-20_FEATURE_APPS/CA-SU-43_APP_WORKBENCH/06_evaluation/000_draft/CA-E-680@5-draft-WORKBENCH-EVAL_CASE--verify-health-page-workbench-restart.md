---
identity:
  atom_id: CA-E-680
  ref_id: CA-E-680@5-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Execution Control
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-R-2782
  IS_REPLACEMENT_FOR:
  - CA-E-680
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T20:47:43.495627+00:00'
destination:
  file:
    name: CA-E-680@5-draft-WORKBENCH-EVAL_CASE--verify-health-page-workbench-restart.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/06_evaluation/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
---
## Summary

Verify health-page Workbench restart

## Claim

### Prose Claim

Verify that the health-page Restart Workbench action invokes the same native MCP action and displays the actual ready or failure result. The page remains available on failure. GET HTML and JSON are read-only.

For a fixed Project, verify that the form yields fresh queries, unknown old result IDs and loadable saved items. An invalid Declaration reports failure without disabling MCP or the page.

On a shared host, verify that the form requires an explicit Project folder and restarts only that Project. Missing, repeated or unknown fields are rejected before any effect, and the blacklist remains enforced.
