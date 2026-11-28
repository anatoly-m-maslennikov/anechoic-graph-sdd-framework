---
atom_family: SPEC
atom_id: AN-S-5195
concern:
  subject: Filesystem
  path: Model/Carrier
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 1
  updated_at: "2026-11-28T11:52:02.110048+00:00"
---

## Summary

Declare Filesystem

## Semantics

A Filesystem holds Files and Folders at named paths.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(Filesystem, Carrier)
```
