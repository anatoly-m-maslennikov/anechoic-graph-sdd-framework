---
atom_family: SPEC
atom_id: AN-S-3133
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.248235+00:00"
---

## Summary

Declare Prefix

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ProjectManifest, Property

class Property3133(Property):
    name = 'Prefix'
    bearer = ProjectManifest
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```

## Semantics

Prefix identifies the Project namespace in its Atom IDs. Record the Operator’s uppercase Prefix in the Project Manifest before creating the first native Atom. Validate it as written.
