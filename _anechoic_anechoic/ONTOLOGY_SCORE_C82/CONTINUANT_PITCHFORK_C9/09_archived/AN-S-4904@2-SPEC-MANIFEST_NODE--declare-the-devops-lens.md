---
atom_family: SPEC
atom_id: AN-S-4904
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.373448+00:00"

---

## Summary

Declare the DevOps Lens

## Semantics

Groups how the Project builds, delivers, deploys, and operates its realization.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/DevOps Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class DevOpsLens(Lens):
    node.lens_path = value(fixed='DevOps')
```
