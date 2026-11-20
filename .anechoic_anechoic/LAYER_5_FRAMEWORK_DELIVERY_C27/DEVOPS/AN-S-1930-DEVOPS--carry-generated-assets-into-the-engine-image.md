---
identity:
  atom_id: AN-S-1930
context:
  container:
    component: C27
  tier: 4
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: '2026-11-12T09:56:54.214180+00:00'
---
## Summary

Carry generated assets into the Engine image

## Claim

### Prose Claim

Build the image with the exact Workbench schema, relation registry, Tool registry, lifecycle status model and lifecycle candidate schema in its build context. Existing mode copies these files from the checkout as-is. Refresh mode replaces the set with verified compiler output and records the files at the next Local Release Git checkpoint. The build uses the supplied files unchanged.
