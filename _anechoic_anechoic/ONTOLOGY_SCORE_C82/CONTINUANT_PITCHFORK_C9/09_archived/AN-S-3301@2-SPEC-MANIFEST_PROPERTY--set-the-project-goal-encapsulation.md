---
atom_family: SPEC
atom_id: AN-S-3301
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.520736+00:00'
---

## Summary

Set the Project Goal encapsulation

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Purpose//Project Goal.Encapsulation

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, ProjectGoal, Property

class Property3301(Property):
    name = 'Encapsulation'
    bearer = Atom
    allowed_values = ('white_box', 'black_box')
    applies_to_entity_classes = (ProjectGoal,)
    field_options = {'class_var': True, 'default': 'black_box'}
    value_format = str
```
