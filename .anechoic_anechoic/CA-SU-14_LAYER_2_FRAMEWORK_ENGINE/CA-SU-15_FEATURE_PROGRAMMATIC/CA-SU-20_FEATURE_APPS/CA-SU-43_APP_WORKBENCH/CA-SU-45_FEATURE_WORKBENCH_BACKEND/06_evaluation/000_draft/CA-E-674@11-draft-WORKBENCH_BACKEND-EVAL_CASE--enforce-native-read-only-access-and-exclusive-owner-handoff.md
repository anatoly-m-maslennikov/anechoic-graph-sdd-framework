---
identity:
  atom_id: CA-E-674
  ref_id: CA-E-674@11-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Query Processing
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-R-2728
  - CA-M-462
  - CA-M-463
  IS_REPLACEMENT_FOR:
  - CA-E-674
state:
  status: draft
  version: 11
  updated_at: '2026-11-13T22:31:23.061386+00:00'
destination:
  file:
    name: CA-E-674@11-draft-WORKBENCH_BACKEND-EVAL_CASE--enforce-native-read-only-access-and-exclusive-owner-handoff.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
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

Verify that trusted public SQL uses native single-query admission and trusted internal materialization.

## Details

- It executes the exact SQL once, returns complete bounded results or explicit errors,
  and shares serialized access with indexing.
- Public SQL cannot edit sources or projected source rows.
- Owned database and spill writes are permitted.

### MVP limitations

The MVP provides no function sandbox.

- External file and network access, retry, rollback, and recovery are unsupported.
- DuckPGQ management functions may invalidate the connection.

### Test cases

Verify that each case preserves source bytes:

- Native `SELECT`, CTE, and `GRAPH_TABLE` queries succeed.
- Multi-statement SQL, DDL, DML, `SET`, `COPY`, and `ATTACH` are rejected.
- External access fails. The connection remains usable after invalid SQL.
- A DuckPGQ management function can invalidate the connection.
- Under a memory limit, DuckDB spills to disk or returns a resource error.
- After the query completes, indexing refreshes the data.
  Owner release makes the refreshed state visible.
