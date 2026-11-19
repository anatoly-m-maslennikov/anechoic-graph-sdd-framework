---
atom_id: CA-R-2478
ref_id: CA-R-2478
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//IS_CONTAINED_BY
tier: 3
status: Active
version: 5
updated_at: 2026-11-03 20:00:05 +0400
carrier_destination:
  file:
    name: CA-R-2478-CORE_META_MODEL-DECLARATION--define-composition-and-its-inverse.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2478-CORE_META_MODEL-DECLARATION--define-composition-and-its-inverse.md
  source_atom_id: CA-R-2478
  source_atom_revision: 5
  source_sha256: 0e2c2da34ff192321cb7a3e7723421d512ff032623c4411590f2eb8d6fa85384
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define composition and its inverse

## Claim

### Prose Claim

IS_CONTAINED_BY relates a contained declared Entity or instance to its immediate Container. Containment does not imply narrowing or inheritance. CONTAINS is its derived inverse: its Host and Target are the direct Target and Host, respectively. Store the direct fact once.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_CONTAINED_BY",
    inverse_alias="CONTAINS",
    source_endpoint={"level": "model_entities_or_instances"},
    target_endpoint={"level": "model_entities_or_instances"},
    written_alias="+>",
    reverse_written_alias="<+",
)
```

