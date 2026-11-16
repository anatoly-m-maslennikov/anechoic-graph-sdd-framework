---
identity:
  atom_id: CA-P-3070
  ref_id: CA-P-3070
context:
  container:
    scope_unit: CA-SU-43
  role: plan
  form: plan
  label: Epic
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Storage <+ Temporary State
  tier: 3
state:
  status: backlog
  version: 1
  updated_at: '2026-11-15T17:01:38.157379+00:00'
destination:
  file:
    name: CA-P-3070-EPIC--persist-the-workbench-archive-and-isolate-heavy-parsing.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/03_plan/001_backlog
---
## Summary

Persist the Workbench Archive and isolate heavy parsing

## Objective

Make the full Archive queryable with lower Workbench memory use and faster restarts.

## Scope

Move the P
roject's Workbench database to `.caprmedio_runtime/duckdb/projection.duckdb` and retain the indexed Archive across restarts. Keep fast Atom ID and version lookups, plus the highest Atom number per Role.

Measure memory retained by Archive parsing and optional Python modules. Evaluate a short-lived Archive parsing worker with Workbench as the sole DuckDB writer.

## Definition of Done

- Verify full Archive queries, exact revision lookup, and allocation summaries after restart and after source changes.
- Measure first-load peak RAM, idle RAM after import, restart time, and query and watcher performance against the current Workbench.
- Record the worker and import decisions in RMEDO and verify the changes through Workbench E2E tests.
