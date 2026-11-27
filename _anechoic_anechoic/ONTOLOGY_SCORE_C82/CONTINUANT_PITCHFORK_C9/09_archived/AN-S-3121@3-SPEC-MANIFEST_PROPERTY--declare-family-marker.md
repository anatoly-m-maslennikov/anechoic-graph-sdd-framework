---
atom_family: SPEC
atom_id: AN-S-3121
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.168584+00:00"
---

## Summary

Declare Family Marker

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification.Family Marker

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, SpecAtom

class Property3121(Property):
    name = 'Family Marker'
    bearer = Atom
    property.applies_to = (SpecAtom,)
    field_options = {'class_var': True, 'default': 'S'}
    property.value.format = str
```
