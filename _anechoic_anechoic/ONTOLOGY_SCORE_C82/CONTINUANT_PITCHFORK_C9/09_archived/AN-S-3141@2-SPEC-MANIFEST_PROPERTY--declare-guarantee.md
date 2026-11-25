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
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.427644+00:00'
---

## Summary

Declare Guarantee

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Contract.Guarantee

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Contract, Property

class Property3141(Property):
    name = 'Guarantee'
    bearer = Contract
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = str
```
