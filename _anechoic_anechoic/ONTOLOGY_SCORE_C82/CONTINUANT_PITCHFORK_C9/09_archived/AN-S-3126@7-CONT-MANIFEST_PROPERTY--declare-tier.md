---
atom_family: SPEC
atom_id: AN-S-3126
concern:
  subject: Tier
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest.Header
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 7
  updated_at: "2026-11-26T15:52:32.329852+00:00"
---

## Summary

Declare Tier

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Property, SpecAtom

class Property3126(Property):
    name = 'Tier'
    bearer = SpecAtom.Header
    property.value.allowed = (1,)
    property.applies_to = (ComponentManifest,)
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = int
```
