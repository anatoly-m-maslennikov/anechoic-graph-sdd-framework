---
atom_id: CA-R-2465
ref_id: CA-R-2465@5-draft
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/Step
tier: 3
status: Draft
version: 5
updated_at: 2026-11-05 02:41:45 +0400
carrier_destination:
  file:
    name: CA-R-2465@5-draft-CORE_META_MODEL-DECLARATION--declare-step.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
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
