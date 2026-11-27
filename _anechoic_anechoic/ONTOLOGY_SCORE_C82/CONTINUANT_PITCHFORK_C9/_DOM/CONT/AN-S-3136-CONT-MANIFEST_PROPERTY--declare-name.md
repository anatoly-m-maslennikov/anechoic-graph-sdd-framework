---
atom_family: SPEC
atom_id: AN-S-3136
concern:
  subject: Name
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
  version: 4
  updated_at: "2026-11-26T15:52:32.644120+00:00"
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
