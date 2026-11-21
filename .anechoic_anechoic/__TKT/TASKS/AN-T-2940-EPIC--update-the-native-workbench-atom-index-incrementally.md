---
atom_family: TKT
atom_id: AN-T-2940
structure:
  container:
    component: C43
  priority: 2
context:
  template: epic
state:
  status: active
  version: 1
  updated_at: '2026-11-21T08:39:00.116641+00:00'
---
## Summary

Update the native Workbench Atom index incrementally

## Objective

Publish Atom folder changes and their relation edges together. Read only the changed Markdown files for ordinary edits. Use the existing full rebuild for startup, repair, and projection schema changes.

Configure journal and Workbench table storage independently. Use NDJSON files or an on-disk DuckDB table for the Work Journal. Use on-disk or in-memory DuckDB for other Workbench tables. All disk-backed tables share the Project database file delivered in AN-T-2922.

## Definition of Done

- Verify create, edit, rename, and delete on the packaged native runtime.
- Record visibility times and verify the Local Release test gates.
- Verify that journal entries survive restart and projection rebuild in every storage combination. Keep the journal table outside the graph.
