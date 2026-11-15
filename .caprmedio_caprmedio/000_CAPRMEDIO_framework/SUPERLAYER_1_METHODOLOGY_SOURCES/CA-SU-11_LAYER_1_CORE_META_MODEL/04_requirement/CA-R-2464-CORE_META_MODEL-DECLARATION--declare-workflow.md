---
atom_id: CA-R-2464
ref_id: CA-R-2464
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/Workflow
tier: 3
status: active
version: 10
updated_at: '2026-11-13T22:58:40.301878+00:00'
container:
  scope_unit: CA-SU-11
destination:
  file:
    name: CA-R-2464-CORE_META_MODEL-DECLARATION--declare-workflow.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
---

## Summary

Declare Workflow

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Operations

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
