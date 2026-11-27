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
  version: 4
  updated_at: "2026-11-26T15:54:02.242138+00:00"
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
