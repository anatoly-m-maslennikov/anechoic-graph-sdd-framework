---
atom_family: SPEC
atom_id: AN-S-4812
concern:
  subject: Folder
  path: Model/Carrier
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: archived
  version: 4
  updated_at: '2026-11-26T17:13:27.060267+00:00'
---

## Summary

Declare Folder

## Semantics

A Folder represents an entity through a directory assigned to that entity.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(Folder, Carrier)
```
