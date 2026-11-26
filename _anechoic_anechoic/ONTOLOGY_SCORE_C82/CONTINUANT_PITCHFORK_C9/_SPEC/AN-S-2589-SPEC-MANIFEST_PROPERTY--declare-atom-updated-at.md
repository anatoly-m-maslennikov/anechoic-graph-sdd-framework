---
atom_family: SPEC
atom_id: AN-S-2589
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 8
  updated_at: "2026-11-25T19:30:50.490905+00:00"
---
## Summary

Declare Atom.Updated At

## Semantics

Updated At records when this Atom revision was created or last edited. The date-time identifies one instant and includes its UTC offset.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from datetime import datetime

class Property2589(Property):
    name = 'Updated At'
    bearer = Atom.Header.State
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = datetime
```
