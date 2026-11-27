---
atom_family: SPEC
atom_id: AN-S-5052
concern:
  subject: Form
  path: Model/Graph/Node//Artifact//SSOT//Realization/Content/Module/Unit
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: active
  version: 1
  updated_at: '2026-11-27T10:52:53.677257+00:00'
---

## Summary

Declare Unit Form

## Semantics

Form identifies the source construct represented by a Unit. It lets a
Concern select functions and methods within a Module.

## Formal Manifest

```python anechoic-edsl
from anechoic.model import Property, Unit

class UnitForm(Property):
    name = 'Form'
    bearer = Unit
    field_options = {'kw_only': True}
    property.value.format = str
    property.value.allowed = ('class', 'function', 'method')
```
