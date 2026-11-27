---
atom_family: SPEC
atom_id: AN-S-3119
concern:
  subject: Atom ID
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
  version: 7
  updated_at: "2026-11-26T15:52:32.092307+00:00"
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
