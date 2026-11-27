---
atom_family: SPEC
atom_id: AN-S-4904
concern:
  subject: DevOps
  path: Model/Graph/Lens//SPEC//SWE
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T18:18:20.888256+00:00"
---

## Summary

Declare the DevOps Lens

## Semantics

Groups how the Project builds, delivers, deploys, and operates its realization.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SoftwareEngineeringLens

class DevOpsLens(SoftwareEngineeringLens):
    node.lens_path = value(fixed='DevOps')
```
