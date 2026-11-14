---
atom_id: CA-R-2555
ref_id: CA-R-2555
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Package.structural_level
tier: 3
status: active
version: 4
updated_at: '2026-11-13T22:53:30.315950+00:00'
carrier_destination:
  file:
    name: CA-R-2555-CORE_META_MODEL-DECLARATION--declare-package-structural-level.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Declare Package.structural_level

## Claim

### Prose Claim

Project Package has structural_level 0. A contained Package has structural_level one greater than its containing Package.

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name='structural_level',
    relation_name="IS_PROPERTY_OF",
    base_path='Package',
    property_occurrence_cardinality=1, value_format=int, value_cardinality=1, dependent_property_cardinality=0, minimum_value=0,
)
```

