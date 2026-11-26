---
atom_family: SPEC
atom_id: AN-S-3168
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.473899+00:00'
---

## Summary

Declare Container

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Container

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3168(Property):
    name = 'Container'
    bearer = Atom.Header
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = dict[str, str]
```
