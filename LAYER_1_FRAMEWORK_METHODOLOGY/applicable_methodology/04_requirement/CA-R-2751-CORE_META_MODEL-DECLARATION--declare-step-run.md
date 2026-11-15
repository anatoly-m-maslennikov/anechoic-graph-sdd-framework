---
atom_id: CA-R-2751
ref_id: CA-R-2751
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Step Run
tier: 3
status: active
version: 1
updated_at: 2026-11-05 05:27:06 +0400
carrier_destination:
  file:
    name: CA-R-2751-CORE_META_MODEL-DECLARATION--declare-step-run.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2751-CORE_META_MODEL-DECLARATION--declare-step-run.md
  source_atom_id: CA-R-2751
  source_atom_revision: 1
  source_sha256: 9b980c49db7a842c60f83b583463ad46439a1fcb6317f6e631ba7e28f038280d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Step Run

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Execution

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
