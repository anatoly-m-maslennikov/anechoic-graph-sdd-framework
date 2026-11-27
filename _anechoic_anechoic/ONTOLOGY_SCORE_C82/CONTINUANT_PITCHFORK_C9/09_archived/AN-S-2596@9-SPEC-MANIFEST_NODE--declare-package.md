---
atom_family: SPEC
atom_id: AN-S-2596
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 9
  updated_at: "2026-11-26T14:46:18.709436+00:00"
---

## Summary

Declare Package

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Realization/Structure/Package

## Semantics

A local Package kind follows the postfix of its folder name. The reserved postfixes are `__tests`, `__agentic`, and `__assets`.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Realization

class Package(Realization):
    pass
```
