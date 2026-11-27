---
atom_family: SPEC
atom_id: AN-S-2027
concern:
  subject: Happened At
  path: Model/Graph/Node//Artifact//SSOT//Recorded//Event Record
  relation: is_property_of
container:
  component: C9
tier: 3
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:30.359443+00:00"
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

