---
atom_family: SPEC
atom_id: AN-S-1363
container:
  component: C45
tier: 4
context:
  lens: SWD
relations:
  IS_REFERENCE:
  - AN-S-3116@1
state:
  status: "archived"
  version: 12
  updated_at: "2026-11-22T07:35:21.710180+00:00"
---
## Summary

Keep DuckDB Projection ownership in the existing server.

## Claim scope

The derived DuckDB Projection and query results for one Project.

## Claim

### Prose Claim

- Use one serialized Workbench owner and the delivered database and spill paths.
- A second writer process exits with an explicit lock error.
- Serialize refresh, Run, Page, and Check in the existing owner.
- Add no database server, queue, planner, scheduler, or worker.
- Keep parsed-source rows and signatures for incremental refresh.
- Remove cached parse data for deleted, excluded, or invalid sources.
- Treat later source changes as new input.
- Add no configuration staging, second cache, or discarded-state restoration.

- Materialize each Run once in a result table in the configured Workbench database.
- Page reads the snapshot, including after an ordinary source refresh.
- Keep execution and delivery failures separate.
- Measure the startup TTL with a monotonic clock.
- Keep a result while it is young, pinned by its View, or needed by a live result.
- Keep source snapshots through every level of a live result's dependencies.
- Closing a View unpins its snapshot. The normal retention rules still apply.
- Add no heartbeat, cross-process lease, or crash recovery.
- Keep the snapshot when the Operator edits View SQL.
- Release the prior result ID when a valid rerun starts, even if execution fails.
- Clear result tables, IDs, and View bindings at startup.
- Remove an unrevealed result if first-page conversion fails.
- Report later conversion or export errors. Keep the known result ID.

- Rebuild affected live snapshots from the last executed SQL and effective options.
- Use current inputs when rebuilding one result table or all tables.
- Rebuild source snapshots before their dependents.
- Publish replacement IDs, View bindings, and pins together.
- Preserve unsynced View SQL when its snapshot changes.
- Return the old-to-new ID map to the caller.
- Repeat neither save nor export during a rebuild.
