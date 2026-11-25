---
atom_family: SPEC
atom_id: AN-S-3139
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:37.908786+00:00"
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
