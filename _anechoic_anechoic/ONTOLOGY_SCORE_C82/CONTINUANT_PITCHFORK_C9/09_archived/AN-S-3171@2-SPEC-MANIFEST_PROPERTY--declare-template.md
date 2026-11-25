---
atom_family: SPEC
atom_id: AN-S-3171
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.480951+00:00'
---

## Summary

Declare Template

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Context.Template

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3171(Property):
    name = 'Template'
    bearer = Atom.Header.Context
    field_options = {'default': None, 'kw_only': True}
    value_format = str | None
```
