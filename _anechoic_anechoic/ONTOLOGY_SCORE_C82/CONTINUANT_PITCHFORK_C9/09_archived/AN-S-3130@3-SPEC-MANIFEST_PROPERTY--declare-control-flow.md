---
atom_family: SPEC
atom_id: AN-S-3130
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.229541+00:00"
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
