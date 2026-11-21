---
atom_family: TKT
atom_id: AN-T-2754
structure:
  container:
    component: C43
  priority: 2
context:
  template: task
  label: Epic
state:
  status: backlog
  version: 1
  updated_at: '2026-11-15T17:01:38.157379+00:00'
---
## Summary

Persist the Workbench Archive and isolate heavy parsing

## Objective

Make the full Archive queryable with lower Workbench memory use and faster restarts.

## Scope

Move the P
roject's Workbench database to `.anechoic_runtime/duckdb/projection.duckdb` and retain the indexed Archive across restarts. Keep fast Atom ID and version lookups, plus the highest Atom number per Role.

Measure memory retained by Archive parsing and optional Python modules. Evaluate a short-lived Archive parsing worker with Workbench as the sole DuckDB writer.

## Definition of Done

- Verify full Archive queries, exact revision lookup, and allocation summaries after restart and after source changes.
- Measure first-load peak RAM, idle RAM after import, restart time, and query and watcher performance against the current Workbench.
- Record the worker and import decisions in RMEDO and verify the changes through Workbench E2E tests.
