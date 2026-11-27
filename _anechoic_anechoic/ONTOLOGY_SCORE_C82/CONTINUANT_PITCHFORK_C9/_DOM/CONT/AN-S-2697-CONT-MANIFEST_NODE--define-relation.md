---
atom_family: SPEC
atom_id: AN-S-2697
concern:
  subject: Relation
  path: Model/Graph
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 23
  updated_at: '2026-11-26T16:50:11.835470+00:00'
---

## Summary

Define Relation

## Semantics

Each authored Relation fact states one registered direct meaning between its source and target and has one authoritative declaration. Derived Relations identify their derivation and authoritative input facts, including through an upstream Projection. A derived inverse exposes the same fact with the endpoints reversed.

