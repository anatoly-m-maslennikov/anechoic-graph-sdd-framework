---
atom_family: SPEC
atom_id: AN-S-3123
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.187148+00:00"
---

## Summary

Declare Family Marker

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//project_config.Family Marker

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, ProjectConfigAtom, Property

class Property3123(Property):
    name = 'Family Marker'
    bearer = Atom
    property.applies_to = (ProjectConfigAtom,)
    field_options = {'class_var': True, 'default': 'C'}
    property.value.format = str
```
