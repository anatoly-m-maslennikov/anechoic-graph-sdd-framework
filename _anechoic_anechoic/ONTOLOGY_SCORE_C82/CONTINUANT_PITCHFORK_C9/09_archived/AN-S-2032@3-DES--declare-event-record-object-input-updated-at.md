---
atom_family: SPEC
atom_id: AN-S-2032
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T09:25:48.677661+00:00"
---
## Summary

Declare Event Record.object_input.updated_at

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from datetime import datetime

declare_entity(
    entity_name='updated_at',
    relation_name='IS_PROPERTY_OF',
    base_path='Event Record.object_input',
    value_format=datetime,
    property_occurrence_cardinality=1,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

