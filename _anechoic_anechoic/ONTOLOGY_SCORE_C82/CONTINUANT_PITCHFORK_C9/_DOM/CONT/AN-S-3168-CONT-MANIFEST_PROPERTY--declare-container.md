---
atom_family: SPEC
atom_id: AN-S-3168
concern:
  subject: Container
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 6
  updated_at: "2026-11-26T15:52:33.580345+00:00"
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
