---
atom_family: SPEC
atom_id: AN-S-4898
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.206076+00:00"

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
