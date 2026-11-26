---
atom_family: SPEC
atom_id: AN-S-4906
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.403286+00:00"

---

## Summary

Declare the SPEC Lens

## Semantics

Groups definitions and constraints that specify the Model and its instances.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/Specification Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class SpecificationLens(Lens):
    node.lens_path = value(fixed='SPEC')
```
