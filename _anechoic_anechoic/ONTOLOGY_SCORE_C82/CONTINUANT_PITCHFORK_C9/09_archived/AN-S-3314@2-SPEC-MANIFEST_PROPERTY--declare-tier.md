---
atom_family: SPEC
atom_id: AN-S-3314
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.527240+00:00'
---

## Summary

Declare Tier

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Contract//Project Contract.Header.Tier

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ProjectContract, Property, SpecAtom

class Property3314(Property):
    name = 'Tier'
    bearer = SpecAtom.Header
    allowed_values = (0,)
    applies_to_entity_classes = (ProjectContract,)
    field_options = {'kw_only': True}
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = int
```
