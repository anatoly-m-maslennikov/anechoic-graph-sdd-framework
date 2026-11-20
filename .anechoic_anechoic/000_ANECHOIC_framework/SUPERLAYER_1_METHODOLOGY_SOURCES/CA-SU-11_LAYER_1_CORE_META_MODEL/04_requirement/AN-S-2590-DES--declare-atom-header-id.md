---
identity:
  atom_id: AN-S-2590
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-13T22:53:30.315950+00:00'
---
## Summary

Declare Atom.Header.ID

## Claim

### Prose Claim

The ID is immutable when the Atom Status belongs to Current, Backlog, or Archived Status Group.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='ID',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.Identity',
    property_occurrence_cardinality=1, value_format=str, value_cardinality=1, dependent_property_cardinality=0,
)
```

