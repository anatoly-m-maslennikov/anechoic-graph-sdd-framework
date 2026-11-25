---
atom_family: SPEC
atom_id: AN-S-3144
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T16:00:37.940360+00:00"
---

## Summary

Declare Solution

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentSeedManifest, Property

class Property3144(Property):
    name = 'Solution'
    bearer = ComponentSeedManifest
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
