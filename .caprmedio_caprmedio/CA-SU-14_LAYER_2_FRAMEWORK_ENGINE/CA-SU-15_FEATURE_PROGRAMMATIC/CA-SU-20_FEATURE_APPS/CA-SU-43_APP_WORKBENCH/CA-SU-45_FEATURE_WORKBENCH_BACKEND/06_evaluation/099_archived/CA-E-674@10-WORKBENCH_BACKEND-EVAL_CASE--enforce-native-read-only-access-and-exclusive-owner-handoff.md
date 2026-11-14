---
identity:
  atom_id: CA-E-674
  ref_id: CA-E-674@10
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Query Processing
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-R-2728
  - CA-M-462
  - CA-M-463
  IS_REPLACEMENT_FOR:
  - CA-E-674
state:
  status: archived
  version: 10
  updated_at: '2026-11-13T20:53:53.520734+00:00'
destination:
  file:
    name: CA-E-674@10-WORKBENCH_BACKEND-EVAL_CASE--enforce-native-read-only-access-and-exclusive-owner-handoff.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/099_archived
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Enforce native read-only access and exclusive owner handoff

## Claim scope

The public-SQL guard for the file-backed DuckDB Projection.

## Claim

### Prose Claim

Verify that trusted public SQL uses native single-query admission and trusted internal materialization. It executes exact SQL once, returns complete bounded results or explicit errors, and shares serialized access with indexing. Public SQL cannot edit sources or projected source rows; owned database and spill writes are permitted. External file and network access, retry, rollback and recovery are unsupported. DuckPGQ management functions may invalidate the connection. This is an explicit MVP limitation, not a promised function sandbox.

## Details

Exercise native SELECT, CTE and GRAPH_TABLE success; rejection of multi-statement, DDL, DML, SET, COPY and ATTACH input; external-access failure; invalid-SQL recovery; connection-invalidating management failure; bounded-memory spill or resource error; and completion followed by source refresh. Each case preserves source bytes. Owner release makes successful refreshed state visible.
