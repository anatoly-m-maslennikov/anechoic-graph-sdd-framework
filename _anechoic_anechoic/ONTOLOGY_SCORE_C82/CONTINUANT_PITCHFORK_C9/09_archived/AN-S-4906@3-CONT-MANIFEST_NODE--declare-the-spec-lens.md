---
atom_family: SPEC
atom_id: AN-S-4906
concern:
  subject: Specification Lens
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
  updated_at: "2026-11-26T18:00:26.164329+00:00"
---

## Summary

Declare the SPEC Lens

## Semantics

Groups definitions and constraints that specify the Model and its instances.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class SpecificationLens(Lens):
    node.lens_path = value(fixed='SPEC')
```
