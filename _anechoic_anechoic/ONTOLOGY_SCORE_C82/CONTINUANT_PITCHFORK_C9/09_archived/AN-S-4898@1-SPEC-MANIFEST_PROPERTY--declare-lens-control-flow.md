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
  version: 1
  updated_at: "2026-11-25T12:40:53.188438+00:00"
relations:
  IS_REFERENCE:
  - AN-T-3922@1
---

## Summary

Declare Lens Control Flow

## Semantics

A Lens can preset Control Flow for the Spec Atoms that use it.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens.Control Flow

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Lens, Property

class LensControlFlow(Property):
    name = 'Control Flow'
    bearer = Lens
    value_format = str
    allowed_values = ('Declarative', 'Imperative')
```
