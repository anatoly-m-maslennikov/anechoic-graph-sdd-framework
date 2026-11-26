---
atom_family: SPEC
atom_id: AN-S-3120
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:37.786349+00:00"
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
