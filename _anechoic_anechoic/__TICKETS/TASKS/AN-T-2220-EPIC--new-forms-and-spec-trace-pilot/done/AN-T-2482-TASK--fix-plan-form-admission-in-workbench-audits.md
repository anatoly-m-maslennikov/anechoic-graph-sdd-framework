---
atom_family: TKT
atom_id: AN-T-2482
container:
  atom: AN-T-2220
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-13T18:57:31.713906+00:00'
---
## Summary

Fix Plan Form admission in Workbench audits

## Work

Resolve the Plan Form false positive in CA-C-740. Verify that an admitted Plan carrier passes and unsupported Forms and disallowed Role/Form pairs still produce audit diagnostics.