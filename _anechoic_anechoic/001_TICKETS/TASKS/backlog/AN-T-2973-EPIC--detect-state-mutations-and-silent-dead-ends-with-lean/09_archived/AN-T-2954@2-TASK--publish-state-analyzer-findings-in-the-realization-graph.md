---
atom_family: TKT
atom_id: AN-T-2954
container:
  atom: AN-T-2973
priority: 2
context:
  template: task
state:
  status: archived
  version: 2
  updated_at: '2026-11-22T09:53:45.225009+00:00'
---
## Summary

Publish State Analyzer findings in the Realization Graph

## Work

Reuse source discovery, watcher, and DuckDB projection. Publish source-backed state findings against existing Module and Package nodes in Workbench, Console, and MCP. Use the same findings for lint.

## Acceptance

A changed source or grant refreshes affected findings. Lint blocks confirmed violations and reports unresolved effects separately.
