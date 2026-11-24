---
atom_family: TKT
atom_id: AN-T-2945
container:
  atom: AN-T-2944
priority: 2
context:
  template: task
state:
  status: in_queue
  version: 2
  updated_at: "2026-11-22T10:16:51.773176+00:00"
---

## Summary

Declare Code Access in Component Manifests

## Work

Inventory the current Components and their Realization owners. Declare
each Component's allowed imports and exports under `boundaries.code`.
Record its provided and consumed interfaces under `boundaries.io`
and its state reads and writes under `boundaries.state`.

Check that the compiled Structure admits the rules and resolves code
selectors to the intended Packages. Verify the declarations against the
current Realization Graph and the Component's actual interfaces and state.
