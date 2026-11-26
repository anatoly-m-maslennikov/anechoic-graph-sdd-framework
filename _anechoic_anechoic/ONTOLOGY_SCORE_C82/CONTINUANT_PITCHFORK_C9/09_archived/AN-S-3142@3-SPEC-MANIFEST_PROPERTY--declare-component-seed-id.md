---
atom_family: SPEC
atom_id: AN-S-3142
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.429643+00:00'
---

## Summary

Declare Component Seed ID

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Seed Manifest.Component Seed ID

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentSeedManifest, Property

class Property3142(Property):
    name = 'Component Seed ID'
    bearer = ComponentSeedManifest
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = str
```
