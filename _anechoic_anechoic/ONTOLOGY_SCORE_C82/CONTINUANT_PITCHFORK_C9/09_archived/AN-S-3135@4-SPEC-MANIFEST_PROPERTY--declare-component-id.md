---
atom_family: SPEC
atom_id: AN-S-3135
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.262845+00:00"
---

## Summary

Declare Component ID

## Semantics

A Component keeps its ID when its name or folder changes.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Property

class Property3135(Property):
    name = 'Component ID'
    bearer = ComponentManifest
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
