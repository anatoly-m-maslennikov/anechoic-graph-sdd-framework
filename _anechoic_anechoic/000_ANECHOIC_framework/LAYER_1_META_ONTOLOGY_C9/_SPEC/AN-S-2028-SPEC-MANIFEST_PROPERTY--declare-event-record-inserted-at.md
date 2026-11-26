---
atom_family: SPEC
atom_id: AN-S-2028
container:
  component: C9
tier: 3
context:
  lens: SPEC
  template: manifest_property
state:
  status: active
  version: 4
  updated_at: '2026-11-25T21:02:02.963746+00:00'
---
## Summary

Declare Event Record.inserted_at

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import EventRecord, Property
from datetime import datetime

class InsertedAt(Property):
    name = 'Inserted At'
    bearer = EventRecord
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = datetime
    property.dependent_property.cardinality = 0
```

## Semantics

Inserted At records when the Journal accepted the record.

