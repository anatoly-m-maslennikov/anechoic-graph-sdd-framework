---
atom_id: CA-R-2539
ref_id: CA-R-2539
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Projection.Updated At
tier: 3
status: active
version: 3
updated_at: '2026-11-13T22:53:30.315950+00:00'
carrier_destination:
  file:
    name: CA-R-2539-CORE_META_MODEL-DECLARATION--declare-projection-updated-at.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2539-CORE_META_MODEL-DECLARATION--declare-projection-updated-at.md
  source_atom_id: CA-R-2539
  source_atom_revision: 3
  source_sha256: 51b4433729e8da4b2920a945950a7f26a5ff366208ea489f644a1d72644d01c4
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Projection.Updated At

## Claim

### Prose Claim

The Updated At value equals the maximum happened_at among Event Records whose single object_output has no version, has this Projection ID, and has action create or update.

### Formal Claim

```python
from datetime import datetime
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name='Updated At',
    relation_name="IS_PROPERTY_OF",
    base_path='Projection',
    property_occurrence_cardinality=1, value_format=datetime, value_cardinality=1, dependent_property_cardinality=0,
)
```

