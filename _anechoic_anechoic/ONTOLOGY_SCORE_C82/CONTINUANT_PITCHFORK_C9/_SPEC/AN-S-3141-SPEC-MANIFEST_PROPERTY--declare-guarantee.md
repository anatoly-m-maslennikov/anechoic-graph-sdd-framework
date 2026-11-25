---
atom_family: SPEC
atom_id: AN-S-3141
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:37.913549+00:00"
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
