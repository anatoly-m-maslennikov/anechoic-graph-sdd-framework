---
atom_id: CA-R-2581
ref_id: CA-R-2581
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Event Record.Relations
tier: 3
status: active
version: 4
updated_at: '2026-11-13T22:57:24.985880+00:00'
carrier_destination:
  file:
    name: CA-R-2581-CORE_META_MODEL-DECLARATION--declare-event-record-relations.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2581-CORE_META_MODEL-DECLARATION--declare-event-record-relations.md
  source_atom_id: CA-R-2581
  source_atom_revision: 4
  source_sha256: 906eb7d2abba69ee78586ea8721e1255a1c3bce9cc049aedb7b85ab2a2491f95
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Event Record.Relations

## Claim

### Prose Claim

Each immediate dependent Property name is a Relation instance (Relation//$relation).

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Relations',
    relation_name="IS_PROPERTY_OF",
    base_path='Event Record',
    property_occurrence_cardinality=1, value_cardinality=0, dependent_property_cardinality=Cardinality(minimum=0, maximum=None),
)
```
