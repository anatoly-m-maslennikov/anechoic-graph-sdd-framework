---
atom_family: SPEC
atom_id: AN-S-2153
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: 2026-11-05 01:38:59 +0400
---
## Summary

Declare Event

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity, Cardinality
from anechoic.model import Occurrent

class Event(Occurrent):
    pass

declare_entity(
    entity_class=Event,
    entity_name='Event',
    instance_relation_constraints={
        'IS_RECORDED_BY': {"target_entity_paths": ('Event Record',), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        'IS_PRODUCED_BY': {"target_entity_paths": ('Execution',), "targets_per_source": Cardinality(minimum=1, maximum=None)},
    },
)
```

## Semantics

An Event is an occurrence produced by an Execution.
