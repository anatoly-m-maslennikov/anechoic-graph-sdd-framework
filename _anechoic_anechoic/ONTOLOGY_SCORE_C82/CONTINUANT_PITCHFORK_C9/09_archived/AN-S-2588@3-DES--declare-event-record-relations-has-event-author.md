---
atom_family: SPEC
atom_id: AN-S-2588
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T09:25:54.411040+00:00"
---
## Summary

Declare Event Record.Relations.HAS_EVENT_AUTHOR

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Actor

declare_entity(
    entity_name="HAS_EVENT_AUTHOR",
    relation_name="IS_PROPERTY_OF",
    base_path="Event Record.Relations",
    property_occurrence_cardinality=1,
    value_format=Actor,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

