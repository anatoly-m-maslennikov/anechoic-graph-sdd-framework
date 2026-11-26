---
atom_family: SPEC
atom_id: AN-S-2602
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T23:09:48.223812+00:00"
---

## Summary

Declare Step

## Claim

### Prose Claim

Every Step’s Container chain ends at a Workflow. A Step runs one Action or Workflow, or contains one or more nested Steps.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Operations

class Step(Operations):
    pass

declare_entity(
    entity_name='Step', entity_class=Step,
    classifications={'Container': 'yes'},
    instance_relation_constraints={
        'HAS_EXECUTION': {'target_entity_paths': ('Step Run',), 'targets_per_source': Cardinality(minimum=0, maximum=None)},
        'IS_CONTAINED_BY': {'target_entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Workflow', 'Atom/(.Header.Context.Role:=Operations)/Step'), 'targets_per_source': 1},
        'RUNS': {
            'target_entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Action', 'Atom/(.Header.Context.Role:=Operations)/Workflow'),
            'targets_per_source': Cardinality(minimum=0, maximum=1),
        },
        'CONTAINS': {'target_entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Step',)},
    },
)
```

## Semantics

A Step prescribes work within a Workflow.
