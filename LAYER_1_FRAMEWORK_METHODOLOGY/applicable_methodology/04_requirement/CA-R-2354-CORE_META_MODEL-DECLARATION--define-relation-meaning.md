---
atom_id: CA-R-2354
ref_id: CA-R-2354
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation.Meaning
tier: 1
status: active
version: 8
updated_at: '2026-11-12T21:29:33.223207+00:00'
carrier_destination:
  file:
    name: CA-R-2354-CORE_META_MODEL-DECLARATION--define-relation-meaning.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2354-CORE_META_MODEL-DECLARATION--define-relation-meaning.md
  source_atom_id: CA-R-2354
  source_atom_revision: 8
  source_sha256: c14c09f463053b633a0818a88b837d254b064edff6876c1bf0dd3467b2e714da
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Relation Meaning

## Claim

### Prose Claim


Relation Meaning is the canonical meaning of a reusable Relation Type.
### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name="Meaning",
    relation_name="IS_PROPERTY_OF",
    base_path="Relation",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
