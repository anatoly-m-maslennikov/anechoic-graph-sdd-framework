---
atom_family: SPEC
atom_id: AN-S-3132
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T23:12:25.819537+00:00"
---

## Summary

Declare Name

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ProjectManifest, Property

class Property3132(Property):
    name = 'Name'
    bearer = ProjectManifest
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
