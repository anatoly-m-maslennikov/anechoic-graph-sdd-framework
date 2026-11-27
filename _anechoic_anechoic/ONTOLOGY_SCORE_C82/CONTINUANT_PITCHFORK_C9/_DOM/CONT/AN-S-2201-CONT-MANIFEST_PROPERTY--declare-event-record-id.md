---
atom_family: SPEC
atom_id: AN-S-2201
concern:
  subject: ID
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
  updated_at: "2026-11-26T15:52:30.850101+00:00"
---
## Summary

Declare Event Record.ID

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import EventRecord, Property

class EventRecordID(Property):
    name = 'ID'
    bearer = EventRecord
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
    property.dependent_property.cardinality = 0
```

## Semantics

This ID identifies the Event Record. Repeated Journal observations may refer to the same record.
