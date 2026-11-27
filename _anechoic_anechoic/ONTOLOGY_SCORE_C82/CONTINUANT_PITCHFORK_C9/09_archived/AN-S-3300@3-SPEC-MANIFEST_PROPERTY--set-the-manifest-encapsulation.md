---
atom_family: SPEC
atom_id: AN-S-3300
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.651947+00:00"
---

## Summary

Set the Manifest encapsulation

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest.Encapsulation

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Manifest, Property

class Property3300(Property):
    name = 'Encapsulation'
    bearer = Atom
    property.value.allowed = ('white_box', 'black_box')
    property.applies_to = (Manifest,)
    field_options = {'class_var': True, 'default': 'black_box'}
    property.value.format = str
```
