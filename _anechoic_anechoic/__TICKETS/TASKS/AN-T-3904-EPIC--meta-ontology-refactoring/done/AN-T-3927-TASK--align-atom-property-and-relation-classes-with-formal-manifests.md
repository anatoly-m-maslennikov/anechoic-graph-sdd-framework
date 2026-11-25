---
atom_family: TKT
atom_id: AN-T-3927
container:
  atom: AN-T-3904
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-25T16:01:56.577845+00:00"

---
## Summary

Align Atom, Property, and Relation classes with Formal Manifests

## Work

Update Atom, Property, and Relation classes and the eDSL to accept the Atom Relations draft as written. Use the same structure for their formal constraints. Derive the Model address and carrier representation from the declaration where possible.

## Acceptance

Compile the draft unchanged. Validate authored Relation names, Atom reference lists, and cardinalities against the Model. Keep derived edges in the graph projection.

## Verification

The Atom Relations Manifest compiled as written. The loaded Model validated the explicit name and target list rules. Focused eDSL and Model tests passed.
