---
atom_family: SPEC
atom_id: AN-S-2005
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Term Name

## Claim

### Prose Claim

Term.Name is the required word or phrase used as the Term's meaning.
### Formal Claim

```python
# model
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Name',
    relation_name='IS_PROPERTY_OF',
    base_path='Term',
    property_occurrence_cardinality=1,
    value_cardinality=1,
    value_format='str',
    dependent_property_cardinality=0,
)
```

