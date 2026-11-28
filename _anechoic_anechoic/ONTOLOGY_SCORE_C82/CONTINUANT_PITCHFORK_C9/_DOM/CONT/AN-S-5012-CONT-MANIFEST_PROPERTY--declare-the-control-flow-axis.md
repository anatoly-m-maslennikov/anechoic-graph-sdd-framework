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
  status: active
  version: 3
  updated_at: "2026-11-28T11:00:50.522707+00:00"
---

## Summary

Declare the Control Flow Axis

## Semantics

Declarative entities state what holds. Imperative entities state what to do. A Lens uses its effective Control
Flow axis assignment as the preset for SPEC Atoms that use the Lens.

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
