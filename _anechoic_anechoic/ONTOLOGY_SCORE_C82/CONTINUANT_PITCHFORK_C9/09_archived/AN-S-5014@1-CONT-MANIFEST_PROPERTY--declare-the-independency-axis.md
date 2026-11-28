---
atom_family: SPEC
atom_id: AN-S-5014
concern:
  subject: Independency
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

Declare the Independency Axis

## Semantics

A Primary Entity has its own Model declaration. A Property takes its identity from its name and immediate bearer.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Axis, Property

class IndependencyAxis(Property):
    name = 'Independency'
    bearer = Axis
    property.axis = True
    property.value.allowed = ('Primary Entity', 'Property')
```
