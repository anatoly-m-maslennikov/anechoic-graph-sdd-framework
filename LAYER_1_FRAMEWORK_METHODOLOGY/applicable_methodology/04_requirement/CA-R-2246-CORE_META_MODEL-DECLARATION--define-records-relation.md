---
atom_id: CA-R-2246
ref_id: CA-R-2246
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//RECORDS
  dependencies:
  - ANECHOIC_MODEL <+ Event Record
  - ANECHOIC_MODEL <+ Event
tier: 1
status: active
version: 9
updated_at: 2026-11-04 16:07:35 +0400
carrier_destination:
  file:
    name: CA-R-2246-CORE_META_MODEL-DECLARATION--define-records-relation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2246-CORE_META_MODEL-DECLARATION--define-records-relation.md
  source_atom_id: CA-R-2246
  source_atom_revision: 9
  source_sha256: d04ced83f54ea793a8d26b582b7b509486aff127485afbf7514216ba14893423
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define RECORDS Relation

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="RECORDS",
    source_endpoint={"level": "instances", "entity_paths": ("Event Record",)},
    target_endpoint={"level": "instances", "entity_paths": ("Event",)},
    inverse_alias="IS_RECORDED_BY",
)
```

## Semantics

RECORDS is the stored Relation from an Event Record to the Event it describes. Its declared inverse IS_RECORDED_BY is a derived view; an Event Record is distinct from the Event.
