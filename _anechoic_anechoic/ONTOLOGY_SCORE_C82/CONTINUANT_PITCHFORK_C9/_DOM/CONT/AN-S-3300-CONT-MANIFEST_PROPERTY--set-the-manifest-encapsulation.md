---
atom_family: SPEC
atom_id: AN-S-3300
concern:
  subject: Encapsulation
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest
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
  updated_at: "2026-11-26T15:52:34.362644+00:00"
---

## Summary

Set the Manifest encapsulation

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
