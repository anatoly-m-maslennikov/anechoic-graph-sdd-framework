---
atom_family: SPEC
atom_id: AN-S-3136
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.268732+00:00"
---

## Summary

Declare Name

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Property

class Property3136(Property):
    name = 'Name'
    bearer = ComponentManifest
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
