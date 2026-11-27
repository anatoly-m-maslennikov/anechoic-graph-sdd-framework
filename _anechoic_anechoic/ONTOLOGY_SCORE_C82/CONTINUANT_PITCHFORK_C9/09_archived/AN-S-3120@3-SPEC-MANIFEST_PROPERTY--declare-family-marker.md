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
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.162600+00:00"
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
