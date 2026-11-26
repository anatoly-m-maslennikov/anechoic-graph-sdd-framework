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
  version: 2
  updated_at: '2026-11-24T16:58:01.515984+00:00'
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
    allowed_values = ('white_box', 'black_box')
    applies_to_entity_classes = (Contract,)
    field_options = {'class_var': True, 'default': 'black_box'}
    value_format = str
```
