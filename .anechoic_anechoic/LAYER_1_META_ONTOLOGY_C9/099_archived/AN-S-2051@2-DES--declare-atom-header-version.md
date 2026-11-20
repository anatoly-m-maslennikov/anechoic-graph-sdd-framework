---
identity:
  atom_id: AN-S-2051
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Declare Atom.Header.Version

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Version',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.State',
    value_format=int,
    property_occurrence_cardinality=1,
    value_cardinality=1,
    dependent_property_cardinality=0,
    minimum_value=1,
)
```
