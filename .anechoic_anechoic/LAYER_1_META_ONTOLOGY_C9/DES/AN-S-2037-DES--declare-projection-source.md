---
identity:
  atom_id: AN-S-2037
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Projection.Source

## Claim

### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Source',
    relation_name='IS_PROPERTY_OF',
    base_path='Projection',
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=1, maximum=2),
    allowed_dependent_property_names=('Named Selection', 'Atoms'),
)
```

