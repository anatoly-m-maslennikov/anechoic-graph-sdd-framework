---
atom_id: CA-O-240
ref_id: CA-O-240@13
container:
  scope_unit: CA-SU-45
role: Operations
form: Action
topics:
  main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
    <+ Data Handling <+ Query Processing
  dependencies:
  - MODEL//CAPRMEDIO <+ Projection
  - CAPRMEDIO_MODEL <+ Projection
  - CAPRMEDIO_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary
    State
  - CAPRMEDIO_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Architecture <+
    Communication <+ Interface Contracts
tier: 6
relations:
  IS_REPLACEMENT_FOR:
  - CA-O-240
status: archived
version: 13
updated_at: '2026-11-13T20:54:18.945197+00:00'
carrier_destination:
  file:
    name: CA-O-240@13-WORKBENCH_BACKEND-ACTION--execute-one-read-only-duckdb-query.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/09_operations/099_archived
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Execute one read-only DuckDB query

## Operation

### Claim scope

One synchronous public Run or Check request.

### Claim

Execute one whole read-only Run or Check through the selected Project's shared owner. Validate arguments; the cursor is editor metadata. Serialize with refresh, admit one native read query and materialize it once with ordered metadata.

Check returns validity, available exact counts and errors, then discards its result without export, save, log or SQL echo. Run retains ID and counts, saves a Bookmark only after successful execution and submits metadata-only history to the existing writer without waiting.

Direct Run exports the complete cached result in the chosen format by default or an explicit inline page. View Run returns metadata and fetches separately. Return a descriptor only after export succeeds. A later save or export failure preserves the known cached result and reports the failed part without retry or rollback. Ordinary responses omit full SQL; source diagnostics go to stderr.

Validate a View rerun before releasing its old result. Once execution begins, release it even if SQL fails. SQL editing alone preserves the last result. Page and View Fetch use only the existing cache; they never execute, save or log SQL. Explicit Load and View-query reads return SQL.

This Action edits no source Atom or Scope Unit and adds no job, queue, scheduler, retry, rollback or recovery.
