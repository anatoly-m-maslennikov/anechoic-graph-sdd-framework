---
atom_family: SPEC
atom_id: AN-S-3162
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.461506+00:00'
---

## Summary

Declare Atom Family

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Atom Family

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3162(Property):
    name = 'Atom Family'
    bearer = Atom.Header
    allowed_values = ('SPEC', 'TKT', 'PROJECT_CONFIG')
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = str
```
