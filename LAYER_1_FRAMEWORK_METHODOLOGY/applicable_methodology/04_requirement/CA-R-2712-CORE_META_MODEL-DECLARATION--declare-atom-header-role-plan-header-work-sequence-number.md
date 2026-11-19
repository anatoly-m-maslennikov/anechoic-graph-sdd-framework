---
atom_id: CA-R-2712
ref_id: CA-R-2712
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan).Header.Context.Plan.Work
    Sequence Number
tier: 3
status: active
version: 6
updated_at: '2026-11-13T04:24:17.610072+00:00'
carrier_destination:
  file:
    name: CA-R-2712-CORE_META_MODEL-DECLARATION--declare-atom-header-role-plan-header-work-sequence-number.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2712-CORE_META_MODEL-DECLARATION--declare-atom-header-role-plan-header-work-sequence-number.md
  source_atom_id: CA-R-2712
  source_atom_revision: 6
  source_sha256: 43c74990e012b96e0e4378071f8ae89dbe9f23fd5e40ccdf61823b5a554701f8
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Atom/(.Header.Role := Plan).Header.Work Sequence Number

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Work Sequence Number",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom/(.Header.Context.Role:=Plan).Header.Context.Plan",
    value_format=int,
    value_cardinality=Cardinality(minimum=0, maximum=1),
    minimum_value=1,
    dependent_property_cardinality=0,
    population_entity_path="Atom/(.Header.Context.Role:=Plan)",
    population_unique_constraints=(
        {
            "keys": ("Header.Context.Container.atom", "Header.Context.Plan.Work Sequence Number"),
            "status": "Active",
            "single_value_paths": ("Header.Context.Container.atom", "Header.Context.Plan.Work Sequence Number"),
        },
        {
            "keys": ("Header.Context.Container.scope_unit", "Header.Context.Plan.Work Sequence Number"),
            "status": "Active",
            "single_value_paths": ("Header.Context.Container.scope_unit", "Header.Context.Plan.Work Sequence Number"),
        },
    ),
)
```
