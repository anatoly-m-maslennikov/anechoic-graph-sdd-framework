---
atom_family: SPEC
atom_id: AN-S-3197
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 6
  updated_at: "2026-11-25T16:00:38.106762+00:00"
---

## Summary

Declare Tier

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Applicable Principle.Header.Tier

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ApplicablePrinciple, Property, SpecAtom

class Property3197(Property):
    name = 'Tier'
    bearer = SpecAtom.Header
    property.value.allowed = (1, 2)
    property.applies_to = (ApplicablePrinciple,)
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = int
```
