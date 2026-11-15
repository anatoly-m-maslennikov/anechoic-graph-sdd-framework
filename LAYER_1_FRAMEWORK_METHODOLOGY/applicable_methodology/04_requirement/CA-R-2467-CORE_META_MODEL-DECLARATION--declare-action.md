---
atom_id: CA-R-2467
ref_id: CA-R-2467
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/Action
tier: 3
status: active
version: 5
updated_at: '2026-11-13T22:58:40.301878+00:00'
carrier_destination:
  file:
    name: CA-R-2467-CORE_META_MODEL-DECLARATION--declare-action.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2467-CORE_META_MODEL-DECLARATION--declare-action.md
  source_atom_id: CA-R-2467
  source_atom_revision: 5
  source_sha256: 0ec19e3b92707a24c5647192c8b0aa3c4a90cd33d4d5c66d91c8fc64699b5de1
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Action

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Operations

class Action(Operations):
    pass

declare_entity(
    entity_name='Action', entity_class=Action,
    instance_relation_constraints={
        'IS_RUN_BY': {'target_entity_paths': ('Atom/(.Header.Context.Role:=Operations)/Step',), 'targets_per_source': Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

An Action is a reusable operational building block. Its boundary reflects one modeled responsibility.
