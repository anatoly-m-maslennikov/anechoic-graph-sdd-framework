---
atom_id: CA-R-2560
ref_id: CA-R-2560
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ PROJECT STRUCTURE
tier: 3
status: active
version: 3
updated_at: '2026-11-12T20:21:37.628721+00:00'
carrier_destination:
  file:
    name: CA-R-2560-CORE_META_MODEL-DECLARATION--declare-project-structure.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2560-CORE_META_MODEL-DECLARATION--declare-project-structure.md
  source_atom_id: CA-R-2560
  source_atom_revision: 3
  source_sha256: 26fc7368840d36ab8bb22bb51310df51f60b4a4d89f1c1c1580e183722f5fa0c
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare PROJECT STRUCTURE

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Node

class ProjectStructure(Node):
    pass

declare_entity(
    entity_class=ProjectStructure,
    entity_name='PROJECT STRUCTURE',
    model_relation_constraints={"IS_PROPERTY_OF": {"targets_per_source": 0}},
    classifications={"Container": "yes"},
)
```

## Semantics

PROJECT STRUCTURE describes the actual structure of a Project, including its Scope Units, Aspects, and other declared components.
