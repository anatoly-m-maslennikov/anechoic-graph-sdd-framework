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
  version: 1
  updated_at: '2026-11-24T19:28:03+00:00'
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
    classification = True
    allowed_values = ('SSOT', 'Derived')
```
