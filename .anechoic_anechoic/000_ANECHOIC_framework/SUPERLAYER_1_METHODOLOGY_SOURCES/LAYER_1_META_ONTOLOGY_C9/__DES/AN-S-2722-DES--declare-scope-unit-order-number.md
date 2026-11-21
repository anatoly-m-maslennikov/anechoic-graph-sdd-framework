---
atom_family: SPEC
atom_id: AN-S-2722
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T22:57:24.985880+00:00'
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
