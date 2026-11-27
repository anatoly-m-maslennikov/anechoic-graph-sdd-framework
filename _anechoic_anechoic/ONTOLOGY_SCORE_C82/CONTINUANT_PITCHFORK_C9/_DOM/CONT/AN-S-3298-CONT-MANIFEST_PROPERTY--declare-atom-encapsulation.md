---
atom_family: SPEC
atom_id: AN-S-3298
concern:
  subject: Encapsulation
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:34.258027+00:00"
---

## Summary

Declare Atom encapsulation

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
    property.value.allowed = ('white_box', 'black_box')
    field_options = {'class_var': True, 'default': 'white_box'}
    property.value.format = str
```
