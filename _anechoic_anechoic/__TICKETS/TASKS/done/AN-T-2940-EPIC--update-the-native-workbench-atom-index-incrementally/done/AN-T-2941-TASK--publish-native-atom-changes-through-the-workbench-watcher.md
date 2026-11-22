---
atom_family: TKT
atom_id: AN-T-2941
container:
  atom: AN-T-2940
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-21T11:51:30.044652+00:00'
---
## Summary

Publish native Atom changes through the Workbench watcher

## Objective

Read the changed carriers and publish their Atom rows, exact references, and relation edges in one transaction. Keep duplicate and invalid carriers out of the published index.

Validate Project Manifest revisions for the same Project and keep indexing subsequent Atom changes. Apply runtime parameters and write authority at startup.
