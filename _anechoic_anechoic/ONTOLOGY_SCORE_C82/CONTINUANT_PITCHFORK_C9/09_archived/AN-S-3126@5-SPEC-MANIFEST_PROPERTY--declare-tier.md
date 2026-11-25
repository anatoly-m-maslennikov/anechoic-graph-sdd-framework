---
atom_family: SPEC
atom_id: AN-S-3126
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 5
  updated_at: '2026-11-24T16:58:01.401389+00:00'
---

## Summary

Declare Tier

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest.Header.Tier

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Property, SpecAtom

class Property3126(Property):
    name = 'Tier'
    bearer = SpecAtom.Header
    allowed_values = (4,)
    applies_to_entity_classes = (ComponentManifest,)
    field_options = {'kw_only': True}
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = int
```
