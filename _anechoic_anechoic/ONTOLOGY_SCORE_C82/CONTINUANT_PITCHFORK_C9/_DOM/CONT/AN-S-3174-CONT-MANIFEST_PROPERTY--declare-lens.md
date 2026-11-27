---
atom_family: SPEC
atom_id: AN-S-3174
concern:
  subject: Lens
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification.Header.Context
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:33.781630+00:00"
---

## Summary

Declare Lens

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
