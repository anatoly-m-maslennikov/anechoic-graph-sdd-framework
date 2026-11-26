---
atom_family: SPEC
atom_id: AN-S-2146
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T20:23:22.518823+00:00"
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
