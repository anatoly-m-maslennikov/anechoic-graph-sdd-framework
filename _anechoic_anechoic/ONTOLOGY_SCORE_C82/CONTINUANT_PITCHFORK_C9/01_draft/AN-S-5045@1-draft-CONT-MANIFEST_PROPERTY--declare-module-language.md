---
atom_family: SPEC
atom_id: AN-S-5045
concern:
  subject: Language
  path: Model/Graph/Node//Artifact//SSOT//Realization/Content/Module
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T09:44:56+00:00'
---

## Summary

Declare Module Language

## Semantics

Language identifies the programming language of a Module. It is a realization
property, not the filename or a Component-wide language selection.

## Formal Manifest

```python anechoic-edsl
from anechoic.model import Module, Property

class Property5045(Property):
    name = 'Language'
    bearer = Module
    field_options = {'default': None, 'kw_only': True}
    property.value.format = str | None
```
