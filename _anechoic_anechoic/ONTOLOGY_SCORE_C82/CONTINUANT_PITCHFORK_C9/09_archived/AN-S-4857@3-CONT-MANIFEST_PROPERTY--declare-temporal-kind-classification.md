---
atom_family: SPEC
atom_id: AN-S-4857
concern:
  subject: Temporal Kind
  path: Model/Graph/Classification
  relation: classifies
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T18:34:34.842792+00:00"
---

## Summary

Declare Temporal Kind classification

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Classification, Property

class Property4857(Property):
    name = 'Temporal Kind'
    bearer = Classification
    property.classification = True
    property.value.allowed = ('Continuant', 'Occurrent')
```
