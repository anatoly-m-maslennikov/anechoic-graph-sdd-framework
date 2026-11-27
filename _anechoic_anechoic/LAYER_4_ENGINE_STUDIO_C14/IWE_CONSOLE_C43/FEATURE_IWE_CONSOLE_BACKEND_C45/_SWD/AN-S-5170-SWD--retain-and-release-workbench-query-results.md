---
atom_family: SPEC
atom_id: AN-S-5170
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 1
  updated_at: '2026-11-27T17:35:02.210100+00:00'
---

## Summary

Retain and release Workbench query results

## Claim

For materialized Run results and linked View snapshots of the selected Project:

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
