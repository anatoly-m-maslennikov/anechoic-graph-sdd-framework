---
atom_family: SPEC
atom_id: AN-S-2187
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T09:23:11.090434+00:00"
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
