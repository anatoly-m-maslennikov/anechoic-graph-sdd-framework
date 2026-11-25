---
atom_family: SPEC
atom_id: AN-S-3137
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.421517+00:00'
---

## Summary

Declare Layer

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest.Layer

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Property

class Property3137(Property):
    name = 'Layer'
    bearer = ComponentManifest
    field_options = {'default': None}
    value_format = int | None
```
