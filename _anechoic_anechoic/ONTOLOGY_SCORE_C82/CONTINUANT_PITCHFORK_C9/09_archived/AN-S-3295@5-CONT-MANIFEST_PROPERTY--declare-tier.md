---
atom_family: SPEC
atom_id: AN-S-3295
concern:
  subject: Tier
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Contract.Header
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 5
  updated_at: "2026-11-28T10:14:16.621462+00:00"
---

## Summary

Declare Tier

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Contract, Property, SpecAtom

class Property3295(Property):
    name = 'Tier'
    bearer = SpecAtom.Header
    property.value.allowed = (0,)
    property.applies_to = (Contract,)
    property.value.format = int
```
