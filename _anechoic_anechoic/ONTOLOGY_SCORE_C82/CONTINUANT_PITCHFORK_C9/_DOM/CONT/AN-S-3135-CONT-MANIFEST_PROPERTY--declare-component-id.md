---
atom_family: SPEC
atom_id: AN-S-3135
concern:
  subject: Component ID
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:32.592948+00:00"
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
