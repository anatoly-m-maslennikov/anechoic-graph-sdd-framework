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
  version: 5
  updated_at: "2026-11-28T10:14:16.621462+00:00"
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
    property.applies_to = (Manifest,)
    field_options = {'class_var': True, 'default': 'black_box'}
```
