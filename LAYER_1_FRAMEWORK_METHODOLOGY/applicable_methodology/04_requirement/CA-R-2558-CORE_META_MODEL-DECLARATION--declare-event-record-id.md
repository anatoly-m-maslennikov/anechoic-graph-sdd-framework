---
atom_id: CA-R-2558
ref_id: CA-R-2558
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Event Record.ID
tier: 3
status: active
version: 3
updated_at: '2026-11-13T04:32:46.823926+00:00'
carrier_destination:
  file:
    name: CA-R-2558-CORE_META_MODEL-DECLARATION--declare-event-record-id.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2558-CORE_META_MODEL-DECLARATION--declare-event-record-id.md
  source_atom_id: CA-R-2558
  source_atom_revision: 3
  source_sha256: acaf599e81ccdcc1bf6b6f608081c4cdd6399902833d53f028597fa4b3dd629b
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Event Record.ID

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="ID",
    relation_name="IS_PROPERTY_OF",
    base_path="Event Record",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
    population_unique_constraints=({"keys": ("ID",)},),
)
```
