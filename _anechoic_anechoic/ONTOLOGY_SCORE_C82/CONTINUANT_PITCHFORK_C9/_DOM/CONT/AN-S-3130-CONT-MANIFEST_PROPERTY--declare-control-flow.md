---
atom_family: SPEC
atom_id: AN-S-3130
concern:
  subject: Control Flow
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
  updated_at: "2026-11-26T15:52:32.403653+00:00"
---

## Summary

Declare Control Flow

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Manifest, Property

class Property3130(Property):
    name = 'Control Flow'
    bearer = Manifest
    field_options = {'class_var': True, 'default': 'Declarative'}
    property.value.format = str
```
