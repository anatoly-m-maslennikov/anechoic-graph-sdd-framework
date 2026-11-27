---
atom_family: SPEC
atom_id: AN-S-4856
concern:
  subject: Artifact Kind
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
  updated_at: "2026-11-26T18:39:02.314084+00:00"
---

## Summary

Declare the Artifact Kind Axis

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Axis, Property

class Property4856(Property):
    name = 'Artifact Kind'
    bearer = Axis
    property.axis = True
    property.value.allowed = ('Artifact', 'Ephemeral')
```
