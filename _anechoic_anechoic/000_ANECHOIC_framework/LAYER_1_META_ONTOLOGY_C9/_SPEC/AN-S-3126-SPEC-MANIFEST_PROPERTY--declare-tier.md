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
  status: "active"
  version: 6
  updated_at: "2026-11-25T16:00:37.832665+00:00"
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
    property.value.allowed = (4,)
    property.applies_to = (ComponentManifest,)
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = int
```
