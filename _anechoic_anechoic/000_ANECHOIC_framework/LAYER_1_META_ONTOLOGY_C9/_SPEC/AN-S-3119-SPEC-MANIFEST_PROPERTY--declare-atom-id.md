---
atom_family: SPEC
atom_id: AN-S-3119
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 6
  updated_at: "2026-11-25T20:41:49.082301+00:00"
---

## Summary

Declare Atom ID

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3119(Property):
    name = 'Atom ID'
    bearer = Atom.Header
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```

## Semantics

The Atom keeps this ID throughout its lifecycle.
