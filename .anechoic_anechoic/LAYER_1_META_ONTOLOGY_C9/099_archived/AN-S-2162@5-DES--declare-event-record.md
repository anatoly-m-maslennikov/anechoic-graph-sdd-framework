---
identity:
  atom_id: AN-S-2162
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-05 13:47:13 +0400
---
## Summary

Declare Event Record

## Claim

### Prose Claim


An Event Record is immutable.


### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Continuant

class EventRecord(Continuant):
    pass

declare_entity(
    entity_class=EventRecord,
    entity_name="Event Record",
    model_relation_constraints={"IS_PROPERTY_OF": {"targets_per_source": 0}},
    instance_relation_constraints={
        "IS_CONTAINED_BY": {"target_entity_paths": ("Journal",), "targets_per_source": 1},
        "RECORDS": {"target_entity_paths": ("Event",), "targets_per_source": 1},
    },
)
```

## Semantics

An Event Record is a persistent description of an event and its recorded evidence.
