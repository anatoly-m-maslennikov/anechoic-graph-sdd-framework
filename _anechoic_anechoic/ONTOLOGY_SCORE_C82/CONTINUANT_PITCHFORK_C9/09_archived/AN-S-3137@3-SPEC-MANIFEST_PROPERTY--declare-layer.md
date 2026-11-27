---
atom_family: SPEC
atom_id: AN-S-3137
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.273834+00:00"
---

## Summary

Declare Layer

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Property

class Property3137(Property):
    name = 'Layer'
    bearer = ComponentManifest
    field_options = {'default': None}
    property.value.format = int | None
```
