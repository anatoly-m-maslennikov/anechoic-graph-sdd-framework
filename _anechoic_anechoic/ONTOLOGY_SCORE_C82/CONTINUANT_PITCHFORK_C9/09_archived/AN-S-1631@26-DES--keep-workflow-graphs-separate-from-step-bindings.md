---
atom_family: SPEC
atom_id: AN-S-1631
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: "archived"
  version: 26
  updated_at: "2026-11-25T21:47:25.610344+00:00"
---
## Summary

Keep Workflow graphs separate from Step bindings

## Claim

### Prose Claim


a Workflow graph scheme.


A Workflow graph scheme **must** identify Step references, declared order, structural Relations, entry points, and terminal outcomes.

The graph references Step bindings and called definitions. Its declared graph determines control flow; folder nesting and file order **must not** replace it.
