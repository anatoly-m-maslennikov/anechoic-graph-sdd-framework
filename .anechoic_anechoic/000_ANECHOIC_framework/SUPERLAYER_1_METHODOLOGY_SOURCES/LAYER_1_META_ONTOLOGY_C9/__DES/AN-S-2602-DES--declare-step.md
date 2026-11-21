---
atom_family: SPEC
atom_id: AN-S-2602
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-13T23:06:45.575413+00:00'
---

## Summary

Declare Step

## Claim

### Prose Claim

A Step uses exactly one execution mode. It runs one Action or Workflow, or contains one or more nested Steps.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Operations

class Step(Operations):
    pass

declare_entity(
    entity_name='Step', entity_class=Step,
    instance_relation_constraints={
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

A Step is a unit of work within a Workflow. It has exactly one immediate container, either a Workflow or a Step. It runs exactly one Action or Workflow, or contains one or more nested Steps.
