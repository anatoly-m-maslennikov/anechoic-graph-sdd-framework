---
atom_family: SPEC
atom_id: AN-S-2721
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T09:23:11.930187+00:00"
---
## Summary

Declare Scope Unit.order.ordered

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='ordered',
    relation_name='IS_PROPERTY_OF',
    base_path='Scope Unit.order',
    value_format=bool,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

