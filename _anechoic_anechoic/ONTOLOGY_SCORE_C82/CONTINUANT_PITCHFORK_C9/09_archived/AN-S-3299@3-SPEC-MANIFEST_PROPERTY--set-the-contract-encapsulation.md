---
atom_family: SPEC
atom_id: AN-S-3299
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.642821+00:00"
---

## Summary

Set the Contract encapsulation

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Contract.Encapsulation

## Claim

### Prose Claim

A Contract describes externally observable behavior, including UI,
visual output, and programmatic I/O.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Contract, Property

class Property3299(Property):
    name = 'Encapsulation'
    bearer = Atom
    property.value.allowed = ('white_box', 'black_box')
    property.applies_to = (Contract,)
    field_options = {'class_var': True, 'default': 'black_box'}
    property.value.format = str
```
