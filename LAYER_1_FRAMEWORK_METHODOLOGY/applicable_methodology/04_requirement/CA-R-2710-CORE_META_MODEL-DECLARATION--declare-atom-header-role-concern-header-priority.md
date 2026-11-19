---
atom_id: CA-R-2710
ref_id: CA-R-2710
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Concern).Header.Context.Concern.Priority
tier: 3
status: active
version: 3
updated_at: '2026-11-13T00:11:02.013748+00:00'
carrier_destination:
  file:
    name: CA-R-2710-CORE_META_MODEL-DECLARATION--declare-atom-header-role-concern-header-priority.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2710-CORE_META_MODEL-DECLARATION--declare-atom-header-role-concern-header-priority.md
  source_atom_id: CA-R-2710
  source_atom_revision: 3
  source_sha256: 8dea8a205541c0f762fa05c709049887d867917f17fc0fd3d85c1cdd45b0de17
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom/(.Header.Role := Concern).Header.Priority

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Priority",
    relation_name="IS_PROPERTY_OF",
    base_path='Atom/(.Header.Context.Role:=Concern).Header.Context.Concern',
    property_occurrence_cardinality=1,
    value_format="str",
    value_cardinality=1,
    dependent_property_cardinality=0,
    allowed_values=("High", "Medium", "Low"),
)
```
