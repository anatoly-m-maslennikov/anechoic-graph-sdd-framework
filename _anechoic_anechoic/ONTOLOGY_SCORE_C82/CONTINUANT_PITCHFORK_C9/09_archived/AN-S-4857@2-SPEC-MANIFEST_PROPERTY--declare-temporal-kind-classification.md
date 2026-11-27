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
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.064943+00:00"
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
