---
atom_family: SPEC
atom_id: AN-S-3120
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.388472+00:00'
---

## Summary

Declare Family Marker

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Family Marker

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3120(Property):
    name = 'Family Marker'
    bearer = Atom
    field_options = {'class_var': True, 'default': None}
    value_format = str
```
