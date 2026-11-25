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
  status: "active"
  version: 4
  updated_at: "2026-11-25T23:12:26.120607+00:00"
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

## Semantics

Name records the Operator’s chosen Project name before its first native Atom. Preserve its spelling. Derive the control root from the case-folded name.
