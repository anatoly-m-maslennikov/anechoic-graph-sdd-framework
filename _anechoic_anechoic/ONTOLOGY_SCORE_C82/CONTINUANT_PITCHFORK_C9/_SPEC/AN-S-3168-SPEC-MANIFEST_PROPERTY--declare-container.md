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
  status: "active"
  version: 5
  updated_at: "2026-11-25T20:41:50.072797+00:00"
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

## Semantics

The Container identifies one existing immediate owner by stable ID. An Atom owner resolves to its Current revision. Each chain of Atom owners reaches a Component without a cycle.
