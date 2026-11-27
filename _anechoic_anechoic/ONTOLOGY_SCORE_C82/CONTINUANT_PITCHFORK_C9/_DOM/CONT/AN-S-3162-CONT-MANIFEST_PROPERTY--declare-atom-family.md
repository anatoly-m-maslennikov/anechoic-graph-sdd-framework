---
atom_family: SPEC
atom_id: AN-S-3162
concern:
  subject: Atom Family
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
  version: 4
  updated_at: "2026-11-26T15:52:33.431297+00:00"
---

## Summary

Declare Atom Family

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3162(Property):
    name = 'Atom Family'
    bearer = Atom.Header
    property.value.allowed = ('SPEC', 'TKT', 'PROJECT_CONFIG')
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
