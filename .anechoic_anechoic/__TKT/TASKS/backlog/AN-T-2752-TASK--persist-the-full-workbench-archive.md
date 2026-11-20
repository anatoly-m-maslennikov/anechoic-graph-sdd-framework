---
identity:
  atom_id: AN-T-2752
context:
  container:
    atom: AN-T-2754
  tier: 4
  template: task
state:
  status: backlog
  version: 1
  updated_at: '2026-11-15T17:02:13.170219+00:00'
---
## Summary

Persist the full Workbench Archive

## Objective

Update and review RMEDO for the Project-local DuckDB path, full Archive indexing, and fast Atom allocation lookups. Implement and verify the reviewed spec.

## Definition of Done

Full Archive queries and exact revision lookups work after restart. Watcher changes update the Archive rows and allocation summaries. Record first-load peak RAM, idle RAM, and restart time.
