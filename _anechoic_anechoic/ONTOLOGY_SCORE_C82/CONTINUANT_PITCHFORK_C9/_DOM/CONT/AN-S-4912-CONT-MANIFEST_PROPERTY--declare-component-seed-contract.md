---
atom_family: SPEC
atom_id: AN-S-4912
concern:
  subject: Contract
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
  version: 2
  updated_at: "2026-11-26T15:52:36.878667+00:00"
---

## Summary

Declare Component Seed Contract

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import Cardinality
from anechoic.model import ComponentSeedManifest, Property

class ComponentSeedContract(Property):
    name = 'Contract'
    bearer = ComponentSeedManifest
    field_options = {'default': None, 'kw_only': True}
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 1
    property.value.format = str | None
```
