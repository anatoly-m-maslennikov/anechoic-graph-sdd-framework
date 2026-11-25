---
atom_family: SPEC
atom_id: AN-S-3142
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 4
  updated_at: "2026-11-25T16:00:37.920277+00:00"
---

## Summary

Declare Component Seed ID

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentSeedManifest, Property

class Property3142(Property):
    name = 'Component Seed ID'
    bearer = ComponentSeedManifest
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
