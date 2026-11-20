---
identity:
  atom_id: AN-S-1363
context:
  container:
    component: C45
  tier: 4
  lens: SWD
state:
  status: active
  version: 10
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Keep DuckDB Projection ownership in the existing server.

## Claim scope

The derived DuckDB Projection and query results for one Project.

## Claim

### Prose Claim

Keep one serialized DuckDB owner in the existing application. Use the delivered database and spill locations.

Materialize each Run once. Page reads use that materialized result, including after source refresh; execution and delivery retain their separate failure boundaries.

Use the delivered startup TTL to keep a result while it is young or pinned by its open owner View. Measure age with a monotonic clock. Add no heartbeat, cross-process lease or crash recovery. Closing unpins but does not evict a young result. Editing View SQL preserves its last result until valid rerun starts; then release it before native execution, even if SQL fails. Startup rebuild clears old results; IDs do not survive restart. First-page conversion failure removes an unrevealed result; later conversion/export failure preserves the known ID and reports the delivery error.

Serialize refresh, Run, Page and Check through this owner synchronously. Do not add a database server, queue, planner, scheduler or worker. Retain parsed-source rows/signatures for incremental refresh; remove cache for deleted, excluded or invalid sources and treat a later actual change as new input. No configuration staging, second cache or discarded-state restoration is added.
