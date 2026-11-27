---
atom_family: SPEC
atom_id: AN-S-4938
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Recorded//Event Record
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 2
  updated_at: "2026-11-26T15:52:37.072053+00:00"
---
## Summary

Declare Event Record Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import EventRecord, NodeConstraints

class EventRecordConstraints(NodeConstraints):
    bearer = EventRecord
    node.constraints.population_unique = ({'keys': ('ID',)},)
```
