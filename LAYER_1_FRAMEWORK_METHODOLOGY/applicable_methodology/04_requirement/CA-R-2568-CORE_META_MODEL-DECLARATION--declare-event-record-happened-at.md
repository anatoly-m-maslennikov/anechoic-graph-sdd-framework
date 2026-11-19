---
atom_id: CA-R-2568
ref_id: CA-R-2568
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Event Record.happened_at
tier: 3
status: active
version: 3
updated_at: '2026-11-12T12:33:04.158402+00:00'
carrier_destination:
  file:
    name: CA-R-2568-CORE_META_MODEL-DECLARATION--declare-event-record-happened-at.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2568-CORE_META_MODEL-DECLARATION--declare-event-record-happened-at.md
  source_atom_id: CA-R-2568
  source_atom_revision: 3
  source_sha256: 2d9991a1b91262fe1ddab0ceb935dd42d11e1d24d2489108deb19c99e20ad795
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Event Record.happened_at

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from datetime import datetime

declare_entity(
    entity_name='happened_at',
    relation_name='IS_PROPERTY_OF',
    base_path='Event Record',
    value_format=datetime,
    property_occurrence_cardinality=1,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

