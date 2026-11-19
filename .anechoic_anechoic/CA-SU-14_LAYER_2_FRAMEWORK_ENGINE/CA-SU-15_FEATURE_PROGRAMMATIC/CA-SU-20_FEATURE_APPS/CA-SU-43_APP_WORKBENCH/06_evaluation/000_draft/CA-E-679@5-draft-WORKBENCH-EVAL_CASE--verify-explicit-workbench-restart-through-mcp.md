---
identity:
  atom_id: CA-E-679
  ref_id: CA-E-679@5-draft
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
  - CA-E-679
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T20:47:27.713054+00:00'
destination:
  file:
    name: CA-E-679@5-draft-WORKBENCH-EVAL_CASE--verify-explicit-workbench-restart-through-mcp.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/06_evaluation/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
---
## Summary

Verify explicit Workbench restart through MCP

## Claim

### Prose Claim

In one session, run and save a query, restart Workbench through MCP, and run a fresh query. Verify that restart waits for the fresh owner to be ready, the fresh query works, the old Page result ID is rejected, and the saved SQL loads. Verify that sources and saved items are preserved and that the session and unrelated services remain usable.

Verify that invalid startup returns an error without recovery. An invalid Declaration keeps Workbench unavailable until the Declaration is corrected and Workbench is explicitly restarted. In-flight or cancelled work prevents its owner from being closed. Invalid arguments are rejected before any effect. Verify that source bytes, history and MCP tools remain usable.
