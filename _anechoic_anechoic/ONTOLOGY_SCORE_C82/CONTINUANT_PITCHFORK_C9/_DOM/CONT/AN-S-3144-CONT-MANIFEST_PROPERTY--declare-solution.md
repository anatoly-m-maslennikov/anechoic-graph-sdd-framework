---
atom_family: SPEC
atom_id: AN-S-3144
concern:
  subject: Solution
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Seed Manifest
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 6
  updated_at: "2026-11-26T15:52:32.955566+00:00"
---

## Summary

Declare Solution

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import Cardinality
from anechoic.model import ComponentSeedManifest, Property

class Property3144(Property):
    name = 'Solution'
    bearer = ComponentSeedManifest
    field_options = {'default': None, 'kw_only': True}
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 1
    property.value.format = str | None
```
