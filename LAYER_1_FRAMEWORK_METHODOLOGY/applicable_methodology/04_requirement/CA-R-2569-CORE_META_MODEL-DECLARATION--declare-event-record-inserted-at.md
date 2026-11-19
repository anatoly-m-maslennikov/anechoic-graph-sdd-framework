---
atom_id: CA-R-2569
ref_id: CA-R-2569
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Event Record.inserted_at
tier: 3
status: active
version: 3
updated_at: '2026-11-12T12:33:04.158402+00:00'
carrier_destination:
  file:
    name: CA-R-2569-CORE_META_MODEL-DECLARATION--declare-event-record-inserted-at.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2569-CORE_META_MODEL-DECLARATION--declare-event-record-inserted-at.md
  source_atom_id: CA-R-2569
  source_atom_revision: 3
  source_sha256: 249050ca75ec7e8be5b2b6f1bab8214105e014e4a01fca3ec43af48c63580dfc
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Event Record.inserted_at

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from datetime import datetime

declare_entity(
    entity_name='inserted_at',
    relation_name='IS_PROPERTY_OF',
    base_path='Event Record',
    value_format=datetime,
    property_occurrence_cardinality=1,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

