---
atom_id: CA-R-2752
ref_id: CA-R-2752
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Action Run
tier: 3
status: active
version: 1
updated_at: 2026-11-05 05:27:06 +0400
carrier_destination:
  file:
    name: CA-R-2752-CORE_META_MODEL-DECLARATION--declare-action-run.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2752-CORE_META_MODEL-DECLARATION--declare-action-run.md
  source_atom_id: CA-R-2752
  source_atom_revision: 1
  source_sha256: e6fc9b450d2a2e4bc1a22b895d23c7f357be57e40bc2937242b9854aacaaceba
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Action Run

## Claim

### Prose Claim

An Action Run launched by a Step Run is contained by that Step Run.

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Execution

class ActionRun(Execution):
    pass

declare_entity(
    entity_class=ActionRun,
    entity_name='Action Run',
    instance_relation_constraints={
        'IS_EXECUTION_OF': {"target_entity_paths": ('Atom/(.Header.Context.Role:=Operations)/Action',), "targets_per_source": 1},
        'IS_CONTAINED_BY': {"target_entity_paths": ('Step Run',), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

An Action Run is an actual execution of one Action.
