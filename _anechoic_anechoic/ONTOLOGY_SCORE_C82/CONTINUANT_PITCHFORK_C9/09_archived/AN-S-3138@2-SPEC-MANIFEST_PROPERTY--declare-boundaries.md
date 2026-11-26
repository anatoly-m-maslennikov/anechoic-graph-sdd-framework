---
atom_family: SPEC
atom_id: AN-S-3138
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: archived
  version: 2
  updated_at: '2026-11-24T16:58:01.423710+00:00'
---

## Summary

Declare Boundaries

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest.Boundaries

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Property

class Property3138(Property):
    name = 'Boundaries'
    bearer = ComponentManifest
    field_options = {'default': None}
    value_format = dict[str, object] | None
```
