---
atom_family: SPEC
atom_id: AN-S-2197
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T03:54:21.584142+00:00'
---
## Summary

Declare Projection.ID

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="ID", relation_name="IS_PROPERTY_OF", base_path="Projection",
    property_occurrence_cardinality=1, value_format=str, value_cardinality=1,
    dependent_property_cardinality=0,
    population_functional_dependencies=(
        {"keys": ("Form", "Scope Unit"), "dependents": ("ID",)},
        {"keys": ("ID",), "dependents": ("Form", "Scope Unit")},
    ),
)
```

