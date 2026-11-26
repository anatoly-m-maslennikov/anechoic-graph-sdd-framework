---
atom_family: SPEC
atom_id: AN-S-3298
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.513506+00:00'
---

## Summary

Declare Atom encapsulation

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Encapsulation

## Claim

### Prose Claim

Encapsulation describes whether the Atom addresses the implementation
or behavior observable through its interfaces.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3298(Property):
    name = 'Encapsulation'
    bearer = Atom
    allowed_values = ('white_box', 'black_box')
    field_options = {'class_var': True, 'default': 'white_box'}
    value_format = str
```
