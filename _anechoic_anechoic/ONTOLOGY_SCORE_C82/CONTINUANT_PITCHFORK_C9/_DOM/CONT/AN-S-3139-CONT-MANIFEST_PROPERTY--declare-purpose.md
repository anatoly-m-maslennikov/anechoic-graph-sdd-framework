---
atom_family: SPEC
atom_id: AN-S-3139
concern:
  subject: Purpose
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Purpose
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
  updated_at: "2026-11-26T15:52:32.780208+00:00"
---

## Summary

Declare Purpose

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, Purpose

class Property3139(Property):
    name = 'Purpose'
    bearer = Purpose
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
