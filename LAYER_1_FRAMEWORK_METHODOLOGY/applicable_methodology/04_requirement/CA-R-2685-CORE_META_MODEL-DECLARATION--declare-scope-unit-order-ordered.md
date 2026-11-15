---
atom_id: CA-R-2685
ref_id: CA-R-2685
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Scope Unit.order.ordered
  dependencies:
  - CAPRMEDIO_MODEL <+ Scope Unit.order
  - CAPRMEDIO_MODEL <+ Format/bool
tier: 3
status: active
version: 2
updated_at: '2026-11-12T12:33:04.158402+00:00'
container:
  scope_unit: CA-SU-11
destination:
  file:
    name: CA-R-2685-CORE_META_MODEL-DECLARATION--declare-scope-unit-order-ordered.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2685-CORE_META_MODEL-DECLARATION--declare-scope-unit-order-ordered.md
  source_atom_id: CA-R-2685
  source_atom_revision: 2
  source_sha256: 09fb3dc3494f0eee8e779ddb095c0d5d58d68cdc3e3d586aad886bbae55aa951
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Scope Unit.order.ordered

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name='ordered',
    relation_name='IS_PROPERTY_OF',
    base_path='Scope Unit.order',
    value_format=bool,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

