---
atom_family: SPEC
atom_id: AN-S-4857
concern:
  subject: Temporal Kind
  path: Model/Graph/Axis
  relation: has_axis
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T18:39:02.319780+00:00"
---

## Summary

Declare the Temporal Kind Axis

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Axis, Property

class Property4857(Property):
    name = 'Temporal Kind'
    bearer = Axis
    property.axis = True
    property.value.allowed = ('Continuant', 'Occurrent')
```
