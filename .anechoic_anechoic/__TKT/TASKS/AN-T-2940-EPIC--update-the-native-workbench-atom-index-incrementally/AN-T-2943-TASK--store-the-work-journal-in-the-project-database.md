---
atom_family: TKT
atom_id: AN-T-2943
structure:
  container:
    atom: AN-T-2940
  priority: 2
context:
  template: task
state:
  status: active
  version: 1
  updated_at: '2026-11-21T08:53:36Z'
---
## Summary

Store the Work Journal in the Project database

## Objective

Add two independent Project Manifest settings.

- **Work Journal** uses `files` for NDJSON or `duckdb` for a dedicated table in the Project's on-disk DuckDB.
- **Other Workbench tables** use the Project's on-disk DuckDB or live in memory for the lifetime of the runtime.

Use the same Project database file for all disk-backed tables. Keep the journal table outside the graph.

## Definition of Done

- Update the journal storage Spec AN-S-1821 and the existing journal write and read paths.
- Keep existing NDJSON history readable and preserve append order.
- Verify all four combinations and confirm that journal entries survive restart and Workbench projection rebuild in each.
- Verify that in-memory Workbench tables are rebuilt at startup and leave existing durable data intact.
