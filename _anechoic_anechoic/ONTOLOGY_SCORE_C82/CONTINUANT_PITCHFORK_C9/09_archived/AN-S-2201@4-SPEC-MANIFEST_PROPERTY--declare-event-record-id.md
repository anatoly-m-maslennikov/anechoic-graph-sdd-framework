---
atom_family: SPEC
atom_id: AN-S-2201
container:
  component: C9
tier: 3
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:01.877933+00:00"
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
