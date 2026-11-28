---
atom_family: SPEC
atom_id: AN-S-5013
concern:
  subject: Perspective
  path: Model/Graph/Node
  relation: has_axis
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: active
  version: 2
  updated_at: "2026-11-28T10:28:09.160093+00:00"
---

## Summary

Declare the Perspective Axis

## Semantics

To Be states what should hold. As Is describes the realization. Recorded preserves an observation or event.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node, Property

class PerspectiveAxis(Property):
    name = 'Perspective'
    bearer = Node
    property.axis = True
    property.value.allowed = ('To Be', 'As Is', 'Recorded')
```
