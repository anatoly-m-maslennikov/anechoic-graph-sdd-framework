---
atom_id: CA-R-2465
ref_id: CA-R-2465
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/Step
tier: 3
status: active
version: 7
updated_at: '2026-11-13T23:06:45.575413+00:00'
carrier_destination:
  file:
    name: CA-R-2465-CORE_META_MODEL-DECLARATION--declare-step.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2465-CORE_META_MODEL-DECLARATION--declare-step.md
  source_atom_id: CA-R-2465
  source_atom_revision: 7
  source_sha256: 1b67b2a4711231fd2e577c4ed614bf970d48c15fcdf6cbdfe1c18aeff44a100d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
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
