---
identity:
  atom_id: CA-R-3128
  ref_id: CA-R-3128
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  tier: 3
  topics:
    main_subject: ANECHOIC_MODEL <+ Scope Unit.Paths
state:
  version: 1
  status: active
  updated_at: '2026-11-12T22:03:59.156641+00:00'
destination:
  file:
    name: CA-R-3128-CORE_META_MODEL-DECLARATION--declare-scope-unit-paths.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3128-CORE_META_MODEL-DECLARATION--declare-scope-unit-paths.md
  source_atom_id: CA-R-3128
  source_atom_revision: 1
  source_sha256: 1769736a6d9ef3d4595b03e442279259bf59817b25926259d9d9f5815d59f8e4
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Scope Unit Paths

## Claim

### Prose Claim

Paths groups the Scope Unit’s two physical folder paths. Each path is relative to the Project root.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Paths",
    relation_name="IS_PROPERTY_OF",
    base_path="Scope Unit",
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=2,
    allowed_dependent_property_names=("Authority", "Delivery"),
)
```
