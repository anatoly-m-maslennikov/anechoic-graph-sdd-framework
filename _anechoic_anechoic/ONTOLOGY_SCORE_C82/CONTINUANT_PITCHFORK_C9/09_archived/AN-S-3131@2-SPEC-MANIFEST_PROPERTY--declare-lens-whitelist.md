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
  version: 2
  updated_at: '2026-11-24T16:58:01.409404+00:00'
---

## Summary

Declare Lens Whitelist

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest.Lens Whitelist

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Manifest, Property

class Property3131(Property):
    name = 'Lens Whitelist'
    bearer = Manifest
    field_options = {'default': None, 'kw_only': True}
    value_format = list[str] | None
```
