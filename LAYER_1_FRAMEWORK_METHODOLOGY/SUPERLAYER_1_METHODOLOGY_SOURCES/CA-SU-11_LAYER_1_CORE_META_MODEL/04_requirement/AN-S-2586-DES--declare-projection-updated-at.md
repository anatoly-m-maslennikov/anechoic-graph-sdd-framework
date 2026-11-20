---
identity:
  atom_id: AN-S-2586
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

Declare Projection.Updated At

## Claim

### Prose Claim

The Updated At value equals the maximum happened_at among Event Records whose single object_output has no version, has this Projection ID, and has action create or update.

### Formal Claim

```python
from datetime import datetime
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Updated At',
    relation_name="IS_PROPERTY_OF",
    base_path='Projection',
    property_occurrence_cardinality=1, value_format=datetime, value_cardinality=1, dependent_property_cardinality=0,
)
```

