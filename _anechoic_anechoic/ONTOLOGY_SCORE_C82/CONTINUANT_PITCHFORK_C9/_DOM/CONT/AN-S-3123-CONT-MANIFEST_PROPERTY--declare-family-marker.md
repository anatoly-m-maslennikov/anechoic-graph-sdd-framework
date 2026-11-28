---
atom_family: SPEC
atom_id: AN-S-3123
concern:
  subject: Family Marker
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//project_config
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-28T10:14:16.621462+00:00"
---

## Summary

Declare Family Marker

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, ProjectConfigAtom, Property

class Property3123(Property):
    name = 'Family Marker'
    bearer = Atom
    property.applies_to = (ProjectConfigAtom,)
    field_options = {'class_var': True, 'default': 'C'}
```
