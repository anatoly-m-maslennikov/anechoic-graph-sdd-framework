---
identity:
  atom_id: AN-S-2022
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

Declare Projection.Form

## Claim

### Formal Claim

```python
# model
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Form',
    relation_name='IS_PROPERTY_OF',
    base_path='Projection',
    property_occurrence_cardinality=1,
    value_cardinality=1,
    value_format='str',
    dependent_property_cardinality=0,
)
```

