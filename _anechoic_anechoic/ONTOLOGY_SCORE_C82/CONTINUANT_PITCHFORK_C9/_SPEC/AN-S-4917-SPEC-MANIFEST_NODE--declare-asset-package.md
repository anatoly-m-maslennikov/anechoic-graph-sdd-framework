---
atom_family: SPEC
atom_id: AN-S-4917
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: active
  version: 1
  updated_at: "2026-11-25T19:21:22.139580+00:00"
---

## Summary

Declare Asset Package

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Realization/Structure/Package//Asset Package

## Semantics

An Asset Package folder name ends in `__assets`. Its members are Assets carried by non-executable files.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package

class AssetPackage(Package):
    pass
```
