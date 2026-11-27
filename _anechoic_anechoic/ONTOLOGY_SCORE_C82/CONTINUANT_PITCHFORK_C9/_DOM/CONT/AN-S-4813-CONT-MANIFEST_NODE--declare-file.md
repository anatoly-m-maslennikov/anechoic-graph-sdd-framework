---
atom_family: SPEC
atom_id: AN-S-4813
concern:
  subject: File
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
  version: 4
  updated_at: '2026-11-26T17:13:27.508454+00:00'
---

## Summary

Declare File

## Semantics

A File represents content carried as bytes at a filesystem path.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(File, Carrier)
```
