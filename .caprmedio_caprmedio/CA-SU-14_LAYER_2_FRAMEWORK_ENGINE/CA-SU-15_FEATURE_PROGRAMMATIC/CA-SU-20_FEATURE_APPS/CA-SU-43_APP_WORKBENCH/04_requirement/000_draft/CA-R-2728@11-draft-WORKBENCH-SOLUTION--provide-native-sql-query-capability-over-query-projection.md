---
identity:
  atom_id: CA-R-2728
  ref_id: CA-R-2728@11-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Requirement
  form: Solution
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Projection
  tier: 3
state:
  status: draft
  version: 11
  updated_at: '2026-11-14T07:53:12.919343+00:00'
destination:
  file:
    name: CA-R-2728@11-draft-WORKBENCH-SOLUTION--provide-native-sql-query-capability-over-query-projection.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/04_requirement/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-2728
---
## Summary

Provide native SQL query capability over query projection

## Claim

### Prose Claim

Run and Check synchronously against the synchronized Atom Projection.
Each accepts one complete native read-only query.

## Details

- Cursor position is editor metadata. Reject multiple statements. Invalid
  SQL returns a query error distinct from a source-file failure.
- Queries preserve source files and source-derived Projection data.
- `query_schema` exposes actual tables and columns, including declared Content
  and optional distinct non-null Header Status values for escaped completion.
- Schema reads execute no SQL and leave the saved Journal untouched.
- Unsaved Run, Check, and Page have no saved-item effects.
