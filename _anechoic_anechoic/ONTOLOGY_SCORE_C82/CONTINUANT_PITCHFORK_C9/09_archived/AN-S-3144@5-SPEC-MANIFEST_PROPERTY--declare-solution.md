---
atom_family: SPEC
atom_id: AN-S-3144
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T15:54:02.330213+00:00"
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
