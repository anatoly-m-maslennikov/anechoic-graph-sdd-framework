---
atom_family: SPEC
atom_id: AN-S-4938
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:03.543156+00:00"
---
## Summary

Declare Event Record Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Recorded//Event Record.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import EventRecord, NodeConstraints

class EventRecordConstraints(NodeConstraints):
    bearer = EventRecord
    node.constraints.population_unique = ({'keys': ('ID',)},)
```
