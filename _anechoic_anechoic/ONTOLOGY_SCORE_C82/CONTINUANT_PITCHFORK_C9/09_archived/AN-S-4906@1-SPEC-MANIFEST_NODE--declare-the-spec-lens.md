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
  status: "archived"
  version: 1
  updated_at: "2026-11-25T12:40:53.442202+00:00"
relations:
  IS_REFERENCE:
  - AN-T-3922@1
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
    lens_path = value(fixed='SPEC')
```
