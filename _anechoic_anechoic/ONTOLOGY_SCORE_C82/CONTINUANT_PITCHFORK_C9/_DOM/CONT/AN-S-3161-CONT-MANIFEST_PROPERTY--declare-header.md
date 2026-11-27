---
atom_family: SPEC
atom_id: AN-S-3161
concern:
  subject: Header
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:33.394567+00:00"
---

## Summary

Declare Header

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3161(Property):
    name = 'Header'
    bearer = Atom
    property.dependent_property.name.allowed = ('Atom Family', 'Atom ID', 'Concern', 'Container', 'Tier', 'Priority', 'Context', 'Relations', 'State')
    property.dependent_property.ordered_pairs = (('Atom Family', 'Atom ID'), ('Atom ID', 'Concern'), ('Concern', 'Container'), ('Container', 'Tier'), ('Tier', 'Priority'), ('Priority', 'Context'), ('Context', 'Relations'), ('Relations', 'State'))
    property.cardinality = 1
    property.value.cardinality = 0
    property.value.format = object
```
