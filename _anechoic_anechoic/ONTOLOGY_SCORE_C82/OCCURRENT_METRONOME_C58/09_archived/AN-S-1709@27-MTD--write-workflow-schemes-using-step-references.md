---
atom_family: SPEC
atom_id: AN-S-1709
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: "archived"
  version: 27
  updated_at: "2026-11-25T23:01:32.608369+00:00"
---
## Summary

Write Workflow schemes using Step references

## Claim

### Prose Claim


Workflow schemes using Step references.


**to** write a Workflow scheme, express the graph through references **to** its Step Atoms:

- use **`=1`** unambiguous reference for **every** graph node; readable node labels **may** accompany those references.
- state the entry, declared Step order and structural Relations, Conditional Step routing, **and** terminal outcomes against those nodes.
- Declare the invoked Action or Workflow and its parameter and input bindings in the leaf Step Atom. A containing Step groups its Substeps and has no invocation binding of its own.
- Reference reusable Action or Workflow behavior from the Step. Keep its definition at the referenced Atom.

The declared graph determines control flow independently of folder nesting and file order. State each transition's type and its result condition. Give each Workflow, Step, and Action its own primary contribution. For an Action, specify applicable inputs, preconditions, results, effects, and failures. Only a declared Step invocation binds callable behavior. Solutions and Policies describe their own contribution.
