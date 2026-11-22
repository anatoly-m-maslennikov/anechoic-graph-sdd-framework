---
atom_family: TKT
atom_id: AN-T-2192
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: '2026-11-11T23:42:33.311047+00:00'
---
## Summary

Apply Method policies to Atom Lifecycle

## Details

All six MCP actions use the same Project-bound Workbench SQL backend. The shared reads handle exact and batched revisions, ID allocation, and containment. The action does not walk the Project to select Atom files.
