---
atom_family: SPEC
atom_id: AN-S-4857
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.211094+00:00"
---

## Summary

Declare Temporal Kind classification

## Claim scope

MODEL//ANECHOIC <+ Graph/Classification >| Temporal Kind

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
