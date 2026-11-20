---
identity:
  atom_id: AN-S-2170
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T18:51:56.607337+00:00'
---

## Summary

Declare Scope Unit.structural_level

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

def check_structural_level(unit: ScopeUnit) -> bool:
    if unit.structural_level is None:
        return False
    if unit.container is None:
        return unit.structural_level == 0
    return (
        unit.container.structural_level is not None
        and unit.structural_level == unit.container.structural_level + 1
    )

declare_entity(
    entity_name="structural_level",
    relation_name="IS_PROPERTY_OF",
    base_path="Scope Unit",
    property_occurrence_cardinality=1,
    value_format=int,
    value_cardinality=1,
    dependent_property_cardinality=0,
    minimum_value=0,
    instance_check=check_structural_level,
)
```

