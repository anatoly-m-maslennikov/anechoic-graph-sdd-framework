---
atom_family: SPEC
atom_id: AN-S-4897
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T12:40:53.147959+00:00"
relations:
  IS_REFERENCE:
  - AN-T-3922@1
---

## Summary

Declare Lens Path

## Semantics

The full Lens path identifies one Lens in the Project.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens.Lens Path

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Lens, Property

class LensPath(Property):
    name = 'Lens Path'
    bearer = Lens
    value_format = str
```
