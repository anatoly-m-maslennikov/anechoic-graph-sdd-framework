---
atom_family: SPEC
atom_id: AN-S-4898
concern:
  subject: Control Flow
  path: Model/Graph/Lens
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 3
  updated_at: "2026-11-26T15:52:36.522682+00:00"
---

## Summary

Declare Lens Control Flow

## Semantics

A Lens can preset Control Flow for the Spec Atoms that use it.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Lens, Property

class LensControlFlow(Property):
    name = 'Control Flow'
    bearer = Lens
    property.value.format = str
    property.value.allowed = ('Declarative', 'Imperative')
```
