---
atom_family: SPEC
atom_id: AN-S-4856
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.056559+00:00"
---

## Summary

Declare Artifact Kind classification

## Claim scope

MODEL//ANECHOIC <+ Graph/Classification >| Artifact Kind

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Classification, Property

class Property4856(Property):
    name = 'Artifact Kind'
    bearer = Classification
    property.classification = True
    property.value.allowed = ('Artifact', 'Ephemeral')
```
