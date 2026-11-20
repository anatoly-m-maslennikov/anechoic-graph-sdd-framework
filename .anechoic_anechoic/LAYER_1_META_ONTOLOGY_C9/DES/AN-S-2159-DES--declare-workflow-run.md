---
identity:
  atom_id: AN-S-2159
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

Declare Workflow Run

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Execution

class WorkflowRun(Execution):
    pass

declare_entity(
    entity_class=WorkflowRun,
    entity_name="Workflow Run",
    classifications={"Container": "yes"},
    instance_relation_constraints={
        "IS_EXECUTION_OF": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Operations)/Workflow",), "targets_per_source": 1},
        "CONTAINS": {"target_entity_paths": ("Step Run",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

A Workflow Run is an actual execution of one Workflow with supplied inputs and parameters.
