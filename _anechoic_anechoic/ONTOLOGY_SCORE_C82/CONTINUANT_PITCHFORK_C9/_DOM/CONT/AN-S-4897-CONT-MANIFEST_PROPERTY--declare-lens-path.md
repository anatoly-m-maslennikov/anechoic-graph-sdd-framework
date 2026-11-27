---
atom_family: SPEC
atom_id: AN-S-4897
concern:
  subject: Lens Path
  path: Model/Graph/Lens
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 3
  updated_at: "2026-11-26T15:52:36.483867+00:00"
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
