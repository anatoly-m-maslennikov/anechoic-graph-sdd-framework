---
atom_family: SPEC
atom_id: AN-S-3171
concern:
  subject: Template
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Context
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 4
  updated_at: "2026-11-26T15:52:33.691541+00:00"
---

## Summary

Declare Template

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3171(Property):
    name = 'Template'
    bearer = Atom.Header.Context
    field_options = {'default': None, 'kw_only': True}
    property.value.format = str | None
```
