---
identity:
  atom_id: CA-M-516
  ref_id: CA-M-516@4-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Method
  form: Decision
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Query Processing
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
  tier: 4
relations:
  method_for:
  - CA-R-2729
  IS_REPLACEMENT_FOR:
  - CA-M-516
state:
  status: draft
  version: 4
  updated_at: '2026-11-13T22:31:17.173500+00:00'
destination:
  file:
    name: CA-M-516@4-draft-WORKBENCH_BACKEND-DECISION--encode-query-result-files-as-json-matrix-by-default.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/05_method/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Encode query result files as JSON matrix by default

## Claim scope

Shared Workbench query-result serialization.

## Claim

### Prose Claim

JSON matrix is the default result-file format.

## Details

- `columns` stores names once. `rows` stores ordered positional values.
- CSV and TOON are alternatives. All formats use the shared value encoder.
- Export uses the existing materialized result without rerunning SQL.

### Value preservation

- Preserve order, duplicate names, nulls, empty strings, Unicode, source
  newlines, and Formal Claim text.
- Keep cell types and multiline Claims.
  - TOON uses the official codec.
  - CSV uses normal quoting. Unquoted empty represents null. Quoted empty
    represents an empty string.
