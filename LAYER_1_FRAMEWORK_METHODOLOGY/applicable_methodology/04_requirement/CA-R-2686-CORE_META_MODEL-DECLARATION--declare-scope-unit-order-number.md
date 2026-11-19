---
atom_id: CA-R-2686
ref_id: CA-R-2686
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Scope Unit.order.number
  dependencies:
  - ANECHOIC_MODEL <+ Scope Unit.order
  - ANECHOIC_MODEL <+ Scope Unit.order.ordered
  - ANECHOIC_MODEL <+ Format/int
tier: 3
status: active
version: 2
updated_at: '2026-11-13T22:57:24.985880+00:00'
destination:
  file:
    name: CA-R-2686-CORE_META_MODEL-DECLARATION--declare-scope-unit-order-number.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2686-CORE_META_MODEL-DECLARATION--declare-scope-unit-order-number.md
  source_atom_id: CA-R-2686
  source_atom_revision: 2
  source_sha256: da65cde235dbdd05da5c02756f84dc59e2c3c2f0131de5fdbdc688319900eda3
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Scope Unit.order.number

## Claim

### Prose Claim

If order.ordered is true, order.number has exactly one integer value of at least 1; otherwise it has no value.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='number',
    relation_name="IS_PROPERTY_OF",
    base_path='Scope Unit.order',
    value_format=int, value_cardinality=Cardinality(minimum=0, maximum=1), dependent_property_cardinality=0, minimum_value=1,
)
```

## Semantics

`order.ordered` is the Boolean value on the same Scope Unit. `1+` admits integer values of at least 1; `{:1}` requires one value. When order.ordered is false, order.number has no value.

The number is the position among ordered siblings with the same direct parent. Displayed positions do not establish parentage, ownership or Atom authority.
