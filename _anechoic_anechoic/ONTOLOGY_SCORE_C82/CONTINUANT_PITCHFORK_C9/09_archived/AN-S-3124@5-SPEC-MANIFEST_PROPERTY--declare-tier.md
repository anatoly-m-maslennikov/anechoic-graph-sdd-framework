---
atom_family: SPEC
atom_id: AN-S-3124
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T15:54:02.193255+00:00"
---

## Summary

Declare Tier

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, SpecAtom

class Property3124(Property):
    name = 'Tier'
    bearer = SpecAtom.Header
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = int
```
