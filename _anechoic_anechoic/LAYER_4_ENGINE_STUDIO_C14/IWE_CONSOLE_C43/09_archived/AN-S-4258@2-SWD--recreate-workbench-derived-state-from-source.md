---
atom_family: SPEC
atom_id: AN-S-4258
container:
  component: C43
tier: 5
context:
  lens: SWD
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Recreate Workbench derived state from source

## Claim

For `workbench_reread`, close the active Workbench owner, remove the dedicated DuckDB database and its WAL and temporary files, create a new database, create the current Atom and Scope Unit tables and all derived relation, graph and query-result tables, then parse the governed Current and Draft source files directly. Materialize the current derived relations and graph data before reporting readiness. Do not truncate rows in place, retain stale columns, keep the old derived database, delete source files or saved items, or retry automatically. An invalid Scope Unit Declaration prevents readiness; an invalid non-Declaration source follows the existing reader error behavior.

## Details

The operation is one synchronous Workbench service operation. It uses the existing Workbench operation boundary and does not add a scheduler, queue, generic service registry, backup store or business Journal event.
