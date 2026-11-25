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
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.280966+00:00"

---

## Summary

Declare Lens Path

## Semantics

The full Lens path identifies one Lens in the Project.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Lens, Property

class LensPath(Property):
    name = 'Lens Path'
    bearer = Lens
    property.value.format = str
```
