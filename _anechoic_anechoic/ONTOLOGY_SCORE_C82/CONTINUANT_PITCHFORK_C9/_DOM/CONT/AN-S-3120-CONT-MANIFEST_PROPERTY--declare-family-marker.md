---
atom_family: SPEC
atom_id: AN-S-3120
concern:
  subject: Family Marker
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
  updated_at: "2026-11-26T15:52:32.118090+00:00"
---

## Summary

Declare Family Marker

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3120(Property):
    name = 'Family Marker'
    bearer = Atom
    field_options = {'class_var': True, 'default': None}
    property.value.format = str
```
