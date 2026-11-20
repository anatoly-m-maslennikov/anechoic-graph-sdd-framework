---
atom_family: SPEC
atom_id: AN-S-2152
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

Declare Execution

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity, Cardinality
from anechoic.model import Occurrent

class Execution(Occurrent):
    pass

declare_entity(
    entity_class=Execution,
    entity_name='Execution',
    instance_relation_constraints={
        'IS_EXECUTED_BY': {"target_entity_paths": ('Runtime',), "targets_per_source": Cardinality(minimum=1, maximum=None)},
        'PRODUCES': {"target_entity_paths": ('Event',), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

An Execution is the actual performance of work.
