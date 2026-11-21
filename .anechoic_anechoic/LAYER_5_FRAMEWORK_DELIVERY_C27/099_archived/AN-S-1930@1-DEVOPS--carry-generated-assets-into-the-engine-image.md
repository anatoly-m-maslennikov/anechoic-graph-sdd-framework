---
atom_family: SPEC
atom_id: AN-S-1930
structure:
  container:
    component: C27
  tier: 4
context:
  lens: DevOps
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-21T13:08:28.580104+00:00"
---
## Summary

Carry generated assets into the Engine image

## Claim

### Prose Claim

Build the image with the exact Workbench schema, relation registry, Tool registry, lifecycle status model and lifecycle candidate schema in its build context. Existing mode copies these files from the checkout as-is. Refresh mode replaces the set with verified compiler output and records the files at the next Local Release Git checkpoint. The build uses the supplied files unchanged.
