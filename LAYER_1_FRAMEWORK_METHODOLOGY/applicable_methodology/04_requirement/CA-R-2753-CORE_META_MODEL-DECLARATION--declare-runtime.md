---
atom_id: CA-R-2753
ref_id: CA-R-2753
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Runtime
tier: 3
status: active
version: 1
updated_at: 2026-11-05 01:38:59 +0400
carrier_destination:
  file:
    name: CA-R-2753-CORE_META_MODEL-DECLARATION--declare-runtime.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2753-CORE_META_MODEL-DECLARATION--declare-runtime.md
  source_atom_id: CA-R-2753
  source_atom_revision: 1
  source_sha256: f3156bbc77ac16fcb340c5dcc7c45dfceae918bea133d51ff73f1a35f57640e4
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Runtime

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity, Cardinality
from caprmedio.model import Occurrent

class Runtime(Occurrent):
    pass

declare_entity(
    entity_class=Runtime,
    entity_name='Runtime',
    instance_relation_constraints={
        'EXECUTES': {"target_entity_paths": ('Execution',), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

A Runtime is an environment in which Executions run.
