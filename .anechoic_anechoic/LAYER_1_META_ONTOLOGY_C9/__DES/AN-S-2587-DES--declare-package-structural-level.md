---
atom_family: SPEC
atom_id: AN-S-2587
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T22:53:30.315950+00:00'
---
## Summary

Declare Package.structural_level

## Claim

### Prose Claim

Project Package has structural_level 0. A contained Package has structural_level one greater than its containing Package.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='structural_level',
    relation_name="IS_PROPERTY_OF",
    base_path='Package',
    property_occurrence_cardinality=1, value_format=int, value_cardinality=1, dependent_property_cardinality=0, minimum_value=0,
)
```

