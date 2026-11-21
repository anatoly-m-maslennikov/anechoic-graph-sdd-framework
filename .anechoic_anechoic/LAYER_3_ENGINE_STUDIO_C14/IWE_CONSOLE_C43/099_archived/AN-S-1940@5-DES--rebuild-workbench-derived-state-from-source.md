---
atom_family: SPEC
atom_id: AN-S-1940
structure:
  container:
    component: C43
  tier: 4
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-21T10:54:29.562209+00:00"
---
## Summary

Rebuild Workbench derived state from source

## Claim

### Prose Claim

`workbench_reread` synchronously drops/recreates dedicated DuckDB database, WAL/temp files, schema, graph and query-result tables, then rereads Current, Draft, Backlog and previously loaded Archive scopes under the installed schema and registry, and materializes current relations and graph before ready. It preserves source files, saved queries/Views and source Journal, but ephemeral result IDs disappear. It neither retains stale database/columns nor truncates in place; invalid Current Scope Unit Declaration/startup reports explicit failure and leaves Workbench unavailable until another explicit operation, without retry. Invalid ordinary source uses existing reader behavior.

This is one Workbench service operation: no scheduler, queue, generic registry, backup or Business Journal. Expose `workbench_reread({})` in generated Service discovery and the same health POST `/anechoic/health/workbench-reread`; GET remains read-only. MCP/health use identical Project gateway/failure boundary; shared host uses explicit `project_root`, single-project accepts no body. It never restarts MCP/other services/container, and health remains available while Workbench is unavailable.
