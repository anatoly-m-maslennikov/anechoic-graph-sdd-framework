---
atom_family: SPEC
atom_id: AN-S-4904
concern:
  subject: DevOps Lens
  path: Model/Graph/Lens
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T18:00:26.199372+00:00"
---

## Summary

Declare the DevOps Lens

## Semantics

Groups how the Project builds, delivers, deploys, and operates its realization.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class DevOpsLens(Lens):
    node.lens_path = value(fixed='DevOps')
```
