---
identity:
  atom_id: AN-S-1631
context:
  container:
    component: C9
  tier: 2
  lens: DES
state:
  status: active
  version: 26
  updated_at: 2026-11-02 17:54:42 +0400
---
## Summary

Keep Workflow graphs separate from Step bindings

## Claim

### Prose Claim


a Workflow graph scheme.


A Workflow graph scheme **must** identify Step references, declared order, structural Relations, entry points, and terminal outcomes.

The graph references Step bindings and called definitions. Its declared graph determines control flow; folder nesting and file order **must not** replace it.
