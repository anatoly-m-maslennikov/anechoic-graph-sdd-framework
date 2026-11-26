---
atom_family: SPEC
atom_id: AN-S-3136
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.419285+00:00'
---

## Summary

Declare Name

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest.Name

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Property

class Property3136(Property):
    name = 'Name'
    bearer = ComponentManifest
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = str
```
