---
atom_family: SPEC
atom_id: AN-S-3173
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:38.070056+00:00"
---

## Summary

Declare Template

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//project_config.Header.Context.Template

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, ProjectConfigAtom, Property

class Property3173(Property):
    name = 'Template'
    bearer = Atom.Header.Context
    property.applies_to = (ProjectConfigAtom,)
    field_options = {'default': None, 'kw_only': True}
    property.value.format = str | None
```
