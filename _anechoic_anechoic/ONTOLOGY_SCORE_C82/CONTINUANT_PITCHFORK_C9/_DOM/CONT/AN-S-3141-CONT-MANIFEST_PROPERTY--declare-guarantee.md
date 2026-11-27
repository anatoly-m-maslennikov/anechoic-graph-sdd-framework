---
atom_family: SPEC
atom_id: AN-S-3141
concern:
  subject: Guarantee
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Contract
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
  updated_at: "2026-11-26T15:52:32.841061+00:00"
---

## Summary

Declare Guarantee

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Contract, Property

class Property3141(Property):
    name = 'Guarantee'
    bearer = Contract
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
