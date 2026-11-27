---
atom_family: SPEC
atom_id: AN-S-3132
concern:
  subject: Name
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Project Manifest
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:32.480070+00:00"
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
