---
atom_family: SPEC
atom_id: AN-S-3143
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 5
  updated_at: "2026-11-25T18:11:24.559884+00:00"
---

## Summary

Declare Purpose

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import Cardinality
from anechoic.model import ComponentSeedManifest, Property

class Property3143(Property):
    name = 'Purpose'
    bearer = ComponentSeedManifest
    field_options = {'default': None, 'kw_only': True}
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 1
    property.value.format = str | None
```
