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
  status: active
  version: 5
  updated_at: '2026-11-27T01:04:20.461163+00:00'
---

## Summary

Declare Template

## Semantics

A Project Config template declares a fixed Template value for a
Project-owned SPEC. Its Model declaration can set
`node.creation_enabled = value(fixed=False)` to stop new Atoms from
using it. Existing Atoms retain the same Template and validation.

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
