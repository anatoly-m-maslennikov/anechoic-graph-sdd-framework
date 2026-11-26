---
atom_family: SPEC
atom_id: AN-S-2599
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 10
  updated_at: "2026-11-25T23:01:34.222904+00:00"
---

## Summary

Declare Workflow

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Operations

class Workflow(Operations):
    pass

declare_entity(
    entity_name='Workflow', entity_class=Workflow,
    qualification_property_path='Atom.Header.Context.Form',
    project_form_content=True,
    instance_relation_constraints={
        'CONTAINS': {'target_entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Step',), 'targets_per_source': Cardinality(minimum=1, maximum=None)},
        'IS_RUN_BY': {'target_entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Step',), 'targets_per_source': Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

A Workflow defines a graph of Steps for governed work. Its Purpose distinguishes Runtime Workflows from Project Workflows through the selections `Workflow/(.Purpose := Runtime)` and `Workflow/(.Purpose := Project)`.

A Workflow has exactly one Form value, `Workflow`.

Both selections inherit the same Step and Action definitions, graph rules, bindings and execution model. Steps and Actions can be reused by either selection. Purpose concerns use in a Project; reusable Workflow definitions can serve different Project-relative purposes without copying their canonical definition. Purpose does not determine shared or isolated execution context, definition ownership or delivery location.
