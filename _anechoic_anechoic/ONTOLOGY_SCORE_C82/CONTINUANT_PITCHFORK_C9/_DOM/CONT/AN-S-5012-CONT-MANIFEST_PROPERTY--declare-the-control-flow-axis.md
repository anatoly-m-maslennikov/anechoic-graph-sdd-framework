---
atom_family: SPEC
atom_id: AN-S-5012
concern:
  subject: Control Flow
  path: Model/Graph/Axis
  relation: has_axis
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: active
  version: 1
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Declare the Control Flow Axis

## Semantics

Declarative entities state what holds. Imperative entities state what to do.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Axis, Property

class ControlFlowAxis(Property):
    name = 'Control Flow'
    bearer = Axis
    property.axis = True
    property.value.allowed = ('Declarative', 'Imperative')
```
