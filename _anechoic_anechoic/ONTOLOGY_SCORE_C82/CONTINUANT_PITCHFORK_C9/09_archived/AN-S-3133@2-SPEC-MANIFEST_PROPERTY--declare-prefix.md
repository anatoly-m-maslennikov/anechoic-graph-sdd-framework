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
  version: 2
  updated_at: '2026-11-24T16:58:01.413330+00:00'
---

## Summary

Declare Prefix

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Project Manifest.Prefix

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ProjectManifest, Property

class Property3133(Property):
    name = 'Prefix'
    bearer = ProjectManifest
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = str
```
