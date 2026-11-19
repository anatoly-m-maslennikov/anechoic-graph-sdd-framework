---
atom_id: CA-R-2541
ref_id: CA-R-2541
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Projection.Source.Named Selection
tier: 3
status: active
version: 3
updated_at: '2026-11-12T21:17:02.662445+00:00'
carrier_destination:
  file:
    name: CA-R-2541-CORE_META_MODEL-DECLARATION--declare-projection-source-named-selection.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2541-CORE_META_MODEL-DECLARATION--declare-projection-source-named-selection.md
  source_atom_id: CA-R-2541
  source_atom_revision: 3
  source_sha256: 1de0e55907fde3d84ea2c57e505464c10254d4b5646e69ebdac0470d9a68c76e
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Projection.Source.Named Selection

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import NamedSelection

declare_entity(
    entity_name="Named Selection",
    relation_name="IS_PROPERTY_OF",
    base_path="Projection.Source",
    property_occurrence_cardinality=1,
    value_format=NamedSelection,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
