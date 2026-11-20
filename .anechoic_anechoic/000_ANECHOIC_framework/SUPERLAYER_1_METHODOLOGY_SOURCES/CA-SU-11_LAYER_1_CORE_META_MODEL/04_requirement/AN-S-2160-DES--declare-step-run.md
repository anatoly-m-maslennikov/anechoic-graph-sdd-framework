---
identity:
  atom_id: AN-S-2160
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 1
  updated_at: 2026-11-05 05:27:06 +0400
---

## Summary

Declare Step Run

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Execution

class StepRun(Execution):
    pass

declare_entity(
    entity_class=StepRun,
    entity_name='Step Run',
    classifications={"Container": "yes"},
    instance_relation_constraints={
        'IS_EXECUTION_OF': {"target_entity_paths": ('Atom/(.Header.Context.Role:=Operations)/Step',), "targets_per_source": 1},
        'IS_CONTAINED_BY': {"target_entity_paths": ('Workflow Run', 'Step Run'), "targets_per_source": 1},
        'CONTAINS': {"target_entity_paths": ('Step Run', 'Action Run'), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

A Step Run is an actual execution of one Step within a Workflow Run.
