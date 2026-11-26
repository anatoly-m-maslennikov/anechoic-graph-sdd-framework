---
atom_family: SPEC
atom_id: AN-S-3162
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 3
  updated_at: "2026-11-25T16:00:38.004150+00:00"
---

## Summary

Declare Atom Family

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3162(Property):
    name = 'Atom Family'
    bearer = Atom.Header
    property.value.allowed = ('SPEC', 'TKT', 'PROJECT_CONFIG')
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
