---
atom_family: SPEC
atom_id: AN-S-3131
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.236168+00:00"
---

## Summary

Declare Lens Whitelist

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Manifest, Property

class Property3131(Property):
    name = 'Lens Whitelist'
    bearer = Manifest
    field_options = {'default': None, 'kw_only': True}
    property.value.format = list[str] | None
```
