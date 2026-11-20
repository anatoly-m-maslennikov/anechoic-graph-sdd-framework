---
atom_family: SPEC
atom_id: AN-S-2151
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

Declare Runtime

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity, Cardinality
from anechoic.model import Occurrent

class Runtime(Occurrent):
    pass

declare_entity(
    entity_class=Runtime,
    entity_name='Runtime',
    instance_relation_constraints={
        'EXECUTES': {"target_entity_paths": ('Execution',), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

A Runtime is an environment in which Executions run.
