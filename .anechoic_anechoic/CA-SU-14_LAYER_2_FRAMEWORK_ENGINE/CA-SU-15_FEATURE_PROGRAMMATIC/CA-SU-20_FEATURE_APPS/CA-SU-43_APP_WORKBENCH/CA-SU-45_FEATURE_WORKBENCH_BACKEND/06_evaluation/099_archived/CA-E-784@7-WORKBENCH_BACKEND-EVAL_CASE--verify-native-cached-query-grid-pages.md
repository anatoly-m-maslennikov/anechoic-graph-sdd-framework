---
identity:
  atom_id: CA-E-784
  ref_id: CA-E-784@7
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
  tier: 8
relations:
  evaluation_for:
  - CA-M-462
  - CA-R-2953
  - CA-O-240
  IS_REPLACEMENT_FOR:
  - CA-E-784
state:
  status: archived
  version: 7
  updated_at: '2026-11-13T20:54:04.948547+00:00'
destination:
  file:
    name: CA-E-784@7-WORKBENCH_BACKEND-EVAL_CASE--verify-native-cached-query-grid-pages.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/099_archived
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Verify native cached query grid pages

## Claim

### Prose Claim

Against real DuckDB materialized results and the MCP boundary, verify `query_page` and applicable `view_fetch`. Zero-based grid indices address original positions despite duplicate or dotted aliases. Public `rowid` order comes from a hidden snapshot ordinal. CTE, DuckPGQ and preview execute original SQL once through the same ordinal CTAS. Original SQL is retained for execution and Bookmark but omitted from ordinary Run and Page responses.

Verify native ordered sorts with `NULLS LAST` and stable ties; literal case-insensitive `contains` where `%` and `_` are not wildcards; conjunctive filters; original whole-cache column metadata; and single-column group page records with global filtered counts across page splits. Invalid grid keys, shapes, operators, directions, indices or types return an input error without damaging the result identity or a later normal page. Page and fetch use only the retained table, with no replay or second cache.

Exercise MCP and native calls, real page boundaries, cache observability and completed exports and explicit inline pages. JSON matrix, CSV and TOON decode to the selected positional values and columns with exact counts and group metadata. Export never reruns SQL.
