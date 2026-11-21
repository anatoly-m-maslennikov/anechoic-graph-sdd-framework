---
atom_family: SPEC
atom_id: AN-S-2589
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-13T22:53:30.315950+00:00'
---
## Summary

Declare Atom.Header.Updated At

## Claim

### Prose Claim

The Updated At value equals the maximum happened_at among Event Records whose single object_output has a version, has this Atom ID and current Version, and has action create or update.

### Formal Claim

```python
from datetime import datetime
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Updated At',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.State',
    property_occurrence_cardinality=1, value_format=datetime, value_cardinality=1, dependent_property_cardinality=0,
)
```

