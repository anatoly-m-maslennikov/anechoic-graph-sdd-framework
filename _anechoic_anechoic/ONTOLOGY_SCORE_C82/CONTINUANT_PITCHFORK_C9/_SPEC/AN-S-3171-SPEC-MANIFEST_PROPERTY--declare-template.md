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
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:38.058208+00:00"
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
