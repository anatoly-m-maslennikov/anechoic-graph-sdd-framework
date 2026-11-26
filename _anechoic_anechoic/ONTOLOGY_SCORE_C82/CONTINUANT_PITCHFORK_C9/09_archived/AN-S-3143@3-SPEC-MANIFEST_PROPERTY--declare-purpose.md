---
atom_family: SPEC
atom_id: AN-S-3143
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.431608+00:00'
---

## Summary

Declare Purpose

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Seed Manifest.Purpose

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentSeedManifest, Property

class Property3143(Property):
    name = 'Purpose'
    bearer = ComponentSeedManifest
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = str
```
