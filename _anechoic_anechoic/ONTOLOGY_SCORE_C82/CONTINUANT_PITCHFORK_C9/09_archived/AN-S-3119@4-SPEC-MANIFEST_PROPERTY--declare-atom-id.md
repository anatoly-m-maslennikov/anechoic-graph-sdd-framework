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
  status: "archived"
  version: 4
  updated_at: '2026-11-24T16:58:01.386110+00:00'
---

## Summary

Declare Atom ID

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Atom ID

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3119(Property):
    name = 'Atom ID'
    bearer = Atom.Header
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = str
```
