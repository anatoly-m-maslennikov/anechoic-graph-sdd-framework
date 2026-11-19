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
