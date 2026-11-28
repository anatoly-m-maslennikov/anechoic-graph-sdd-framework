---
atom_family: SPEC
atom_id: AN-S-3197
concern:
  subject: Tier
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Applicable Principle.Header
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 8
  updated_at: "2026-11-28T10:14:16.621462+00:00"
---

## Summary

Declare Tier

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ApplicablePrinciple, Property, SpecAtom

class Property3197(Property):
    name = 'Tier'
    bearer = SpecAtom.Header
    property.value.allowed = (1, 2)
    property.applies_to = (ApplicablePrinciple,)
    property.value.format = int
```
