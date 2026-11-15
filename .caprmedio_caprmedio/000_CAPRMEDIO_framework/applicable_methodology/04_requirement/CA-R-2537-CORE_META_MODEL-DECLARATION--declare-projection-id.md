---
atom_id: CA-R-2537
ref_id: CA-R-2537
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Projection.ID
tier: 3
status: active
version: 4
updated_at: '2026-11-13T03:54:21.584142+00:00'
carrier_destination:
  file:
    name: CA-R-2537-CORE_META_MODEL-DECLARATION--declare-projection-id.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2537-CORE_META_MODEL-DECLARATION--declare-projection-id.md
  source_atom_id: CA-R-2537
  source_atom_revision: 4
  source_sha256: 42511bbcf63ef40d40961490900d4e82aa6284acda2eca460978374753da8b90
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Projection.ID

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name="ID", relation_name="IS_PROPERTY_OF", base_path="Projection",
    property_occurrence_cardinality=1, value_format=str, value_cardinality=1,
    dependent_property_cardinality=0,
    population_functional_dependencies=(
        {"keys": ("Form", "Scope Unit"), "dependents": ("ID",)},
        {"keys": ("ID",), "dependents": ("Form", "Scope Unit")},
    ),
)
```

