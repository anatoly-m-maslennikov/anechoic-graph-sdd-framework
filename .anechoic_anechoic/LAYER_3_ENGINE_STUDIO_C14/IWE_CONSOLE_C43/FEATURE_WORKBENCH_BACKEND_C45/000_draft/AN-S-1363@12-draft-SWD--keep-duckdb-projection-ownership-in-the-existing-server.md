---
identity:
  atom_id: AN-S-1363
context:
  container:
    component: C45
  tier: 4
  lens: SWD
state:
  status: "draft"
  version: 12
  updated_at: "2026-11-20T13:05:31.236559+00:00"
---
## Summary

Keep DuckDB Projection ownership in the existing server.

## Claim scope

The derived DuckDB Projection and query results for one Project.

## Claim

### Prose Claim

Keep one serialized DuckDB owner in the existing application. Use the delivered database and spill locations. Store materialized result rows in disk-backed tables in the same Project database. The result lifecycle determines when the owner removes those tables.

Materialize each Run once. Page reads use that materialized result, including after source refresh; execution and delivery retain their separate failure boundaries.

Use the delivered startup TTL to keep a result while it is young or pinned by its open owner View. Measure age with a monotonic clock. Add no heartbeat, cross-process lease or crash recovery. Closing unpins but does not evict a young result. Editing View SQL preserves its last result until valid rerun starts; then release it before native execution, even if SQL fails. Startup clears old results; IDs do not survive restart. First-page conversion failure removes an unrevealed result; later conversion/export failure preserves the known ID and reports the delivery error.

Keep each live result's read-only SQL and effective Run options for an explicit rebuild. Rebuild one selected result or every live result in an all-table rebuild after its inputs are current. Publish replacement result IDs and update their owner Views and pins together.

Serialize refresh, Run, Page and Check through this owner synchronously. Do not add a database server, queue, planner, scheduler or worker. Retain parsed-source rows/signatures for incremental refresh; remove cache for deleted, excluded or invalid sources and treat a later actual change as new input. No configuration staging, second cache or discarded-state restoration is added.

## References

[Disk storage Decision AN-S-3116](./AN-S-3116@1-draft-DES-DECISION--store-native-workbench-duckdb-data-on-disk.md)
