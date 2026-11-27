---
atom_family: SPEC
atom_id: AN-S-2028
concern:
  subject: Inserted At
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
  updated_at: "2026-11-26T15:52:30.395433+00:00"
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

