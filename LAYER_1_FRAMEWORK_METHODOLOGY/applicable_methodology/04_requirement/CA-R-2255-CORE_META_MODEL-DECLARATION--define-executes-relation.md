---
atom_id: CA-R-2255
ref_id: CA-R-2255
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//EXECUTES
  dependencies:
  - ANECHOIC_MODEL <+ Runtime
  - ANECHOIC_MODEL <+ Execution
tier: 1
status: active
version: 10
updated_at: 2026-11-05 03:46:06 +0400
carrier_destination:
  file:
    name: CA-R-2255-CORE_META_MODEL-DECLARATION--define-executes-relation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2255-CORE_META_MODEL-DECLARATION--define-executes-relation.md
  source_atom_id: CA-R-2255
  source_atom_revision: 10
  source_sha256: b9d1d4bb9fb25370b567ab48eeb38e50d14067902fb37838562b49db39f6c1f0
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define EXECUTES Relation

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='EXECUTES',
    source_endpoint={"level": "instances", "entity_paths": ('Runtime',)},
    target_endpoint={"level": "instances", "entity_paths": ('Execution',)},
    inverse_alias='IS_EXECUTED_BY',
)
```

## Semantics

EXECUTES is the stored Relation from a Runtime to an Execution. Its declared inverse IS_EXECUTED_BY is a derived view.
