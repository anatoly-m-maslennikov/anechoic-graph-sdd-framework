---
identity:
  atom_id: CA-E-676
  ref_id: CA-E-676@16
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
  - CA-R-2729
  - CA-R-2724
  - CA-M-462
  - CA-M-463
  - CA-M-464
  - CA-M-465
  - CA-D-672
  - CA-D-673
  - CA-M-516
  IS_REPLACEMENT_FOR:
  - CA-E-676
state:
  status: archived
  version: 16
  updated_at: '2026-11-13T20:53:58.214304+00:00'
destination:
  file:
    name: CA-E-676@16-WORKBENCH_BACKEND-EVAL_CASE--query-native-sql-results-and-typed-relation-expansion.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/099_archived
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Query native SQL results and typed relation expansion

## Claim scope

Native SQL and typed relation expansion over derived Projection rows.

## Claim

### Prose Claim

Verify that native DuckDB and DuckPGQ SQL/PGQ return requested columns, types, counts and complete rows through stable bounded pages. Typed reachability follows materialized direct and declared-derived Relations once and terminates cycles. It neither infers prose links nor synthesizes a second inverse. Graph source tables remain `atoms` and `scope_units`.

## Details

Verify native selections, joins, CTEs, aggregation, ordering, regex and GRAPH_TABLE/MATCH with declared dotted Content columns, exact counts and stable pages. Whole-query admission retains comments, quotes, dollar quotes and CTEs; cursor metadata never selects SQL. Preview uses native `relation.limit(N)`, preserves existing LIMIT and changes execution counts. Without preview, no cap is added. Ordinary responses omit exact SQL, while explicit Bookmark load returns it. Save follows successful execution. Failed execution saves nothing. Failed post-result save returns partial metadata without retry or rollback.

Verify Run, Check and Page and MCP/web parity. Check has metadata and errors only; Page reuses the same cache; saved Views and legacy saved items retain compatibility; query schema reads no SQL or saved item. Default complete export is JSON matrix. CSV and official TOON preserve duplicate aliases, zero rows, null and empty and typed values, and multiline Unicode and Formal Claims. Explicit inline pages match exports. View Run stays metadata-only until fetch. Export failure preserves a known result for later fetch, never reports a failed path and never reruns SQL. Query logs retain metadata, never result rows or files.
