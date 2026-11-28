---
atom_family: SPEC
atom_id: AN-S-4858
concern:
  subject: Authority
  path: Model/Graph/Axis
  relation: has_axis
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 4
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Declare the Authority Axis

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Axis, Property

class Property4858(Property):
    name = 'Authority'
    bearer = Axis
    property.axis = True
    property.value.allowed = ('SSOT', 'Derived')
```
