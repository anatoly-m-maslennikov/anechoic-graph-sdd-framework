---
atom_family: SPEC
atom_id: AN-S-3295
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:38.126756+00:00"
---

## Summary

Declare Tier

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Contract.Header.Tier

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Contract, Property, SpecAtom

class Property3295(Property):
    name = 'Tier'
    bearer = SpecAtom.Header
    property.value.allowed = (0,)
    property.applies_to = (Contract,)
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = int
```
