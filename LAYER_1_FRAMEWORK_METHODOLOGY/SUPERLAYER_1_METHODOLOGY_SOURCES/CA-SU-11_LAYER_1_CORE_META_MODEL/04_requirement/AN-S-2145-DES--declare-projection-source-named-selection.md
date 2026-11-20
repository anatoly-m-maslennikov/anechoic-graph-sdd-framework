---
identity:
  atom_id: AN-S-2145
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T21:17:02.662445+00:00'
---
## Summary

Declare Projection.Source.Named Selection

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import NamedSelection

declare_entity(
    entity_name="Named Selection",
    relation_name="IS_PROPERTY_OF",
    base_path="Projection.Source",
    property_occurrence_cardinality=1,
    value_format=NamedSelection,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
