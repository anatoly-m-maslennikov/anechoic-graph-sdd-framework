---
atom_family: SPEC
atom_id: AN-S-2027
container:
  component: C9
tier: 3
context:
  lens: SPEC
  template: manifest_property
state:
  status: active
  version: 4
  updated_at: '2026-11-25T21:02:02.637142+00:00'
---
## Summary

Declare Event Record.happened_at

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import EventRecord, Property
from datetime import datetime

class HappenedAt(Property):
    name = 'Happened At'
    bearer = EventRecord
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = datetime
    property.dependent_property.cardinality = 0
```

## Semantics

Happened At records when the event occurred. A delay in writing the record leaves this time unchanged.

