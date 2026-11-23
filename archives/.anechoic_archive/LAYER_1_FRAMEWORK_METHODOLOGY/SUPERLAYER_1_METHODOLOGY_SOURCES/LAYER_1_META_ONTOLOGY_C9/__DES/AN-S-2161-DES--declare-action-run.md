---
atom_family: SPEC
atom_id: AN-S-2161
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: 2026-11-05 05:27:06 +0400
---

## Summary

Declare Action Run

## Claim

### Prose Claim

An Action Run launched by a Step Run is contained by that Step Run.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Execution

class ActionRun(Execution):
    pass

declare_entity(
    entity_class=ActionRun,
    entity_name='Action Run',
    instance_relation_constraints={
        'IS_EXECUTION_OF': {"target_entity_paths": ('Atom/(.Header.Context.Role:=Operations)/Action',), "targets_per_source": 1},
        'IS_CONTAINED_BY': {"target_entity_paths": ('Step Run',), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

An Action Run is an actual execution of one Action.
