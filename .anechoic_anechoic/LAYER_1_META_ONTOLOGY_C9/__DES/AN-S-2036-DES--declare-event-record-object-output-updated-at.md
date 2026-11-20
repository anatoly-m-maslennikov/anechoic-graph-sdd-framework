---
atom_family: SPEC
atom_id: AN-S-2036
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Declare Event Record.object_output.updated_at

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from datetime import datetime

declare_entity(
    entity_name='updated_at',
    relation_name='IS_PROPERTY_OF',
    base_path='Event Record.object_output',
    value_format=datetime,
    property_occurrence_cardinality=1,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

