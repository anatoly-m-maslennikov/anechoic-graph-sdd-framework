---
atom_family: SPEC
atom_id: AN-S-4917
concern:
  subject: Asset Package
  path: Model/Graph/Node//Artifact//SSOT//Realization/Structure/Package
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 3
  updated_at: '2026-11-26T17:13:37.947482+00:00'
---

## Summary

Declare Asset Package

## Semantics

An Asset Package folder name ends in `__assets`. Its members are Assets carried by non-executable files.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(AssetPackage, Package)
```
