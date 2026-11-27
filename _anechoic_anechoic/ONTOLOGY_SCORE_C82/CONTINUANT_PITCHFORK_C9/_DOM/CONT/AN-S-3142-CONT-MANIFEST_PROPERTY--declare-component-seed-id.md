---
atom_family: SPEC
atom_id: AN-S-3142
concern:
  subject: Component Seed ID
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Seed Manifest
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
  updated_at: "2026-11-26T15:52:32.874803+00:00"
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
