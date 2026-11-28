---
atom_family: SPEC
atom_id: AN-S-5014
concern:
  subject: Independency
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

Declare the Independency Axis

## Semantics

A Primary Entity has its own Model declaration. A Property takes its identity from its name and immediate bearer.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node, Property

class IndependencyAxis(Property):
    name = 'Independency'
    bearer = Node
    property.axis = True
    property.value.allowed = ('Primary Entity', 'Property')
```
