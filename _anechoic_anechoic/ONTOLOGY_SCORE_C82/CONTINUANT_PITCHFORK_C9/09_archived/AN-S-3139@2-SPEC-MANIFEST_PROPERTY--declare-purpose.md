---
atom_family: SPEC
atom_id: AN-S-3139
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.425686+00:00'
---

## Summary

Declare Purpose

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Purpose.Purpose

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, Purpose

class Property3139(Property):
    name = 'Purpose'
    bearer = Purpose
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = str
```
