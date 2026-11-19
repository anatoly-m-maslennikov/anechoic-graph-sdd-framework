---
atom_id: CA-R-2760
ref_id: CA-R-2760
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//PRODUCES
tier: 1
status: active
version: 1
updated_at: 2026-11-04 16:07:35 +0400
carrier_destination:
  file:
    name: CA-R-2760-CORE_META_MODEL-DECLARATION--declare-produces.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2760-CORE_META_MODEL-DECLARATION--declare-produces.md
  source_atom_id: CA-R-2760
  source_atom_revision: 1
  source_sha256: 38581da6ff9f6ee6b334802e7904bf39872d491d1866d7727459fdcca1ec0a96
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare PRODUCES

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='PRODUCES',
    source_endpoint={"level": "instances", "entity_paths": ('Execution',)},
    target_endpoint={"level": "instances", "entity_paths": ('Event',)},
    inverse_alias='IS_PRODUCED_BY',
)
```

## Semantics

PRODUCES links an Execution to an Event it produced.
