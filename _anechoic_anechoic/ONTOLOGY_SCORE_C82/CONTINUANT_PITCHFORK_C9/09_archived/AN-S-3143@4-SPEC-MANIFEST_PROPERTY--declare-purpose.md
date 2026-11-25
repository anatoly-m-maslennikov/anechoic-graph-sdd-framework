---
atom_family: SPEC
atom_id: AN-S-3143
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T16:00:37.931663+00:00"
---

## Summary

Declare Purpose

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentSeedManifest, Property

class Property3143(Property):
    name = 'Purpose'
    bearer = ComponentSeedManifest
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
