---
atom_family: SPEC
atom_id: AN-S-3121
concern:
  subject: Family Marker
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 4
  updated_at: "2026-11-26T15:52:32.155162+00:00"
---

## Summary

Declare Family Marker

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, SpecAtom

class Property3121(Property):
    name = 'Family Marker'
    bearer = Atom
    property.applies_to = (SpecAtom,)
    field_options = {'class_var': True, 'default': 'S'}
    property.value.format = str
```
