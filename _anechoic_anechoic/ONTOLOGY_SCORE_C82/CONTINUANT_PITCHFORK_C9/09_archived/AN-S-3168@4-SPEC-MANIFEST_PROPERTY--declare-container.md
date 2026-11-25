---
atom_family: SPEC
atom_id: AN-S-3168
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T20:41:50.002492+00:00"
---

## Summary

Declare Container

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3168(Property):
    name = 'Container'
    bearer = Atom.Header
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = dict[str, str]
```
