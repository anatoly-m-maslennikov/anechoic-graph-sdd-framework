---
atom_family: SPEC
atom_id: AN-S-5013
concern:
  subject: Perspective
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
  version: 1
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Declare the Perspective Axis

## Semantics

To Be states what should hold. As Is describes the realization. Recorded preserves an observation or event.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Axis, Property

class PerspectiveAxis(Property):
    name = 'Perspective'
    bearer = Axis
    property.axis = True
    property.value.allowed = ('To Be', 'As Is', 'Recorded')
```
