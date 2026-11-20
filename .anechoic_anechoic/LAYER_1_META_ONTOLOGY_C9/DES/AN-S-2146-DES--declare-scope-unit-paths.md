---
identity:
  atom_id: AN-S-2146
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T22:03:59.156641+00:00'
---
## Summary

Declare Scope Unit Paths

## Claim

### Prose Claim

Paths groups the Scope Unit’s two physical folder paths. Each path is relative to the Project root.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Paths",
    relation_name="IS_PROPERTY_OF",
    base_path="Scope Unit",
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=2,
    allowed_dependent_property_names=("Authority", "Delivery"),
)
```
