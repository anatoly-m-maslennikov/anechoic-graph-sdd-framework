---
atom_family: SPEC
atom_id: AN-S-3174
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.544193+00:00"
---

## Summary

Declare Lens

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification.Header.Context.Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, SpecAtom

class Property3174(Property):
    name = 'Lens'
    bearer = SpecAtom.Header.Context
    field_options = {'default': None, 'kw_only': True}
    property.value.format = str | None
```
