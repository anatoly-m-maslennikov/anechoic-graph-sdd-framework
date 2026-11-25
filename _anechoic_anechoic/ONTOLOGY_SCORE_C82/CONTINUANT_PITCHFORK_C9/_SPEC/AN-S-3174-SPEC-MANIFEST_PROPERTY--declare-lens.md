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
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:38.074607+00:00"
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
