---
atom_id: CA-R-2736
ref_id: CA-R-2736
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Projection.Scope Unit
tier: 3
status: active
version: 2
updated_at: '2026-11-12T23:17:21.180957+00:00'
carrier_destination:
  file:
    name: CA-R-2736-CORE_META_MODEL-DECLARATION--declare-projection-scope-unit.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2736-CORE_META_MODEL-DECLARATION--declare-projection-scope-unit.md
  source_atom_id: CA-R-2736
  source_atom_revision: 2
  source_sha256: 58cab01f140a5372e3a120a4c65acdb2c66e3105770ed4855373e3e79835795e
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Projection.Scope Unit

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import ScopeUnit

declare_entity(
    entity_name="Scope Unit",
    relation_name="IS_PROPERTY_OF",
    base_path="Projection",
    property_occurrence_cardinality=1,
    value_format=ScopeUnit,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

