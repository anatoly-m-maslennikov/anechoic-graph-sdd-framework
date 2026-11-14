---
identity:
  atom_id: CA-M-463
  ref_id: CA-M-463@11-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Method
  form: Decision
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Storage <+ Temporary State
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
  tier: 4
relations:
  method_for:
  - CA-R-2725
  - CA-R-2729
  IS_REPLACEMENT_FOR:
  - CA-M-463
state:
  status: draft
  version: 11
  updated_at: '2026-11-14T00:32:52.424781+00:00'
destination:
  file:
    name: CA-M-463@11-draft-WORKBENCH_BACKEND-DECISION--keep-duckdb-projection-ownership-in-the-existing-server.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/05_method/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Keep DuckDB Projection ownership in the existing server.

## Claim

### Prose Claim

One serialized DuckDB owner in the existing application owns a Project’s
derived Projection and query results.

## Details

- Use the delivered database and spill locations.
- Refresh, Run, Page, and Check share the synchronous owner.
- The existing owner uses one cache and adds no database server, queue,
  planner, scheduler, or worker.

### Query results

- Each Run materializes once. Page reads use that result after source
  refresh as well. Execution and delivery have separate failure boundaries.
- The startup TTL keeps a result while young or pinned by its open View.
  Use a monotonic clock. Closing unpins the result and keeps young results.
  - This uses no heartbeat, cross-process lease, or crash recovery.
- Editing View SQL preserves the last result. An admitted rerun releases it
  before execution, even if SQL fails.
- Startup rebuild clears old results and IDs.
- First-page conversion failure removes the unrevealed result. Later
  conversion or export failure preserves the known ID and reports the error.

### Incremental refresh

- Keep parsed rows and signatures. Remove cached data for deleted, excluded,
  or invalid sources. Treat a later actual change as new input.
- Configuration staging and discarded-state restoration are outside this method.
