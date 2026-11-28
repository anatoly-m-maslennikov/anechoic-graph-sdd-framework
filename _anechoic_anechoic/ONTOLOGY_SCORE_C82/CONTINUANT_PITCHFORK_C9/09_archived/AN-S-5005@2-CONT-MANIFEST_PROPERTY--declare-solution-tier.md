---
atom_family: SPEC
atom_id: AN-S-5005
concern:
  subject: Tier
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Solution.Header
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 2
  updated_at: "2026-11-28T10:14:16.621462+00:00"
---

## Summary

Declare Solution Tier

## Formal Manifest

```python anechoic-edsl
from anechoic.model import Property, Solution, SpecAtom

class Property5005(Property):
    name = 'Tier'
    bearer = SpecAtom.Header
    property.value.allowed = (0,)
    property.applies_to = (Solution,)
    property.value.format = int
```
