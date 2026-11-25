---
atom_family: SPEC
atom_id: AN-S-4838
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T19:21:20.513790+00:00"
---

## Summary

Declare Test Package

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Realization/Structure/Package//Test Package

## Semantics

A Test Package folder name ends in `__tests`. Its members are tests.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package

class TestPackage(Package):
    pass
```
