---
atom_family: SPEC
atom_id: AN-S-5012
concern:
  subject: Control Flow
  path: Model/Graph/Node
  relation: has_axis
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 2
  updated_at: "2026-11-28T10:28:09.160093+00:00"
---

## Summary

Declare the Control Flow Axis

## Semantics

Declarative entities state what holds. Imperative entities state what to do.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node, Property

class ControlFlowAxis(Property):
    name = 'Control Flow'
    bearer = Node
    property.axis = True
    property.value.allowed = ('Declarative', 'Imperative')
```
