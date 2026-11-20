---
atom_family: SPEC
atom_id: AN-S-2044
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T17:23:54+00:00'
---

## Summary

Declare Project.Settings.RMED Review

## Claim

### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='RMED Review',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=0, maximum=2),
    allowed_dependent_property_names=('Context Headroom Fraction', 'Max Atoms'),
)
```

