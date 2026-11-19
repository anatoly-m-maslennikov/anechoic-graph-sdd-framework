---
atom_id: CA-R-2687
ref_id: CA-R-2687
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Scope Unit.order
  dependencies:
  - ANECHOIC_MODEL <+ Scope Unit
tier: 3
status: active
version: 2
updated_at: '2026-11-13T00:35:42.536630+00:00'
container:
  scope_unit: CA-SU-11
destination:
  file:
    name: CA-R-2687-CORE_META_MODEL-DECLARATION--declare-scope-unit-order.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2687-CORE_META_MODEL-DECLARATION--declare-scope-unit-order.md
  source_atom_id: CA-R-2687
  source_atom_revision: 2
  source_sha256: d271ea76a39eb4eed326af0c06d2f353a55dd68a0d52921c0d1a0344b7546d09
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Scope Unit.order

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="order",
    relation_name="IS_PROPERTY_OF",
    base_path="Scope Unit",
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=1, maximum=2),
    allowed_dependent_property_names=("ordered", "number"),
)
```

## Semantics

order groups the Boolean ordered and the conditional number as sibling Properties. The group has no direct value.
