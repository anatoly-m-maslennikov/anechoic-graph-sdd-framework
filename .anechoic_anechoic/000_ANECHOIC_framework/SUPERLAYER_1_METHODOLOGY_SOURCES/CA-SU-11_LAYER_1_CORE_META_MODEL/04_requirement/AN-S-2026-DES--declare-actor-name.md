---
identity:
  atom_id: AN-S-2026
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Actor.Name

## Claim

### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Name',
    relation_name='IS_PROPERTY_OF',
    base_path='Actor',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    value_format='str',
    dependent_property_cardinality=0,
)
```

