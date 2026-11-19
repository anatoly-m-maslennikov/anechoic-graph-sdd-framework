---
atom_id: CA-R-2355
ref_id: CA-R-2355
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation.Name
tier: 1
status: active
version: 8
updated_at: '2026-11-12T21:29:37.101539+00:00'
carrier_destination:
  file:
    name: CA-R-2355-CORE_META_MODEL-DECLARATION--define-relation-name.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2355-CORE_META_MODEL-DECLARATION--define-relation-name.md
  source_atom_id: CA-R-2355
  source_atom_revision: 8
  source_sha256: ac38248309b56c38e256563e31d8cf23d502bee32b0ddfaa440739f1a8e69261
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Relation Name

## Claim

### Prose Claim


Relation Name is the canonical name of a reusable Relation Type.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Name",
    relation_name="IS_PROPERTY_OF",
    base_path="Relation",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
