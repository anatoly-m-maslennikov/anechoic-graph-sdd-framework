---
atom_family: SPEC
atom_id: AN-S-3165
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 4
  updated_at: "2026-11-25T16:00:38.022886+00:00"
---

## Summary

Declare Path

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from anechoic.formal_claims import Cardinality

class Property3165(Property):
    name = 'Path'
    bearer = Atom.Header.Concern
    field_options = {'default': None, 'kw_only': True}
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 1
    property.value.format = str | None
```
