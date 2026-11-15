---
atom_id: CA-R-2686
ref_id: CA-R-2686
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Scope Unit.order.number
  dependencies:
  - CAPRMEDIO_MODEL <+ Scope Unit.order
  - CAPRMEDIO_MODEL <+ Scope Unit.order.ordered
  - CAPRMEDIO_MODEL <+ Format/int
tier: 3
status: active
version: 2
updated_at: '2026-11-13T22:57:24.985880+00:00'
destination:
  file:
    name: CA-R-2686-CORE_META_MODEL-DECLARATION--declare-scope-unit-order-number.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
---
## Summary

Declare Scope Unit.order.number

## Claim

### Prose Claim

If order.ordered is true, order.number has exactly one integer value of at least 1; otherwise it has no value.

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity

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
