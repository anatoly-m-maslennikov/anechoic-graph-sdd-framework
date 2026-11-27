---
atom_family: SPEC
atom_id: AN-S-4858
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.074547+00:00"
---

## Summary

Declare Authority classification

## Claim scope

MODEL//ANECHOIC <+ Graph/Classification >| Authority

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Classification, Property

class Property4858(Property):
    name = 'Authority'
    bearer = Classification
    property.classification = True
    property.value.allowed = ('SSOT', 'Derived')
```
