---
atom_id: CA-R-1498
ref_id: CA-R-1498
container:
  scope_unit: CA-SU-11
role: Requirement
form: Relation Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//RECURSIVELY_CONTAINS
  dependencies:
  - ANECHOIC_MODEL <+ Relation//CONTAINS
tier: 1
status: active
version: 21
updated_at: '2026-11-13T22:48:44.142840+00:00'
carrier_destination:
  file:
    name: CA-R-1498-CORE_META_MODEL-RELATION_DECLARATION--derive-recursive-containment-from-direct-containment.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1498-CORE_META_MODEL-RELATION_DECLARATION--derive-recursive-containment-from-direct-containment.md
  source_atom_id: CA-R-1498
  source_atom_revision: 21
  source_sha256: 83c85e74f49c161c99ddced06f63777294a5cff030843f7717d624fa72acfc8d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Derive Recursive Containment from Direct Containment

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="RECURSIVELY_CONTAINS",
    derived_from="CONTAINS",
    source_endpoint={"level": "model_entities_or_instances"},
    target_endpoint={"level": "model_entities_or_instances"},
)
```

## Semantics

The Host recursively contains the Target when one or more successive `CONTAINS` links lead from Host to Target. Intermediate Entities need only satisfy the endpoint constraints of `CONTAINS`. Derive this Relation from the existing links.
