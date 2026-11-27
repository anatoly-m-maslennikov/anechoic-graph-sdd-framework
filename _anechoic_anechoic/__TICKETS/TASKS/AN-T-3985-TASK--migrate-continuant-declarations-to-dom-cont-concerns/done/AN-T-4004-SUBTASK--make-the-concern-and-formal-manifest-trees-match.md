---
atom_family: TKT
atom_id: AN-T-4004
container:
  atom: AN-T-3985
priority: 2
context:
  template: task
  label: Subtask
state:
  status: "done"
  version: 1
  updated_at: "2026-11-26T17:27:47.381720+00:00"
---

## Summary

Make the Concern and Formal Manifest trees match

## Work

Compare the primary entity and variant paths from Concerns with the Formal Manifest Model.

Split a template-defined variant at its last Property operator. For Axiom, the path is `Atom//Spec Atom//.Header.Context`, the relation is `.`, and the subject is `Template := axiom`. The second `//` specializes Spec Atom.

Support the split path in Concern Path Notation. When continuing from a resolved variant, group the value selection before appending a Property, containment, or specialization step.

List each variant's own and inherited properties separately from the tree. Include fixed values.
