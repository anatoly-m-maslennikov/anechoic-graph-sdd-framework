---
atom_family: SPEC
atom_id: AN-S-2203
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:26:43.916107+00:00"
---
## Summary

Declare Atom/(.Header.Role := Plan).Header.Work Sequence Number

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Work Sequence Number",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom/(.Header.Context.Role:=Plan).Header.Context.Plan",
    value_format=int,
    value_cardinality=Cardinality(minimum=0, maximum=1),
    minimum_value=1,
    dependent_property_cardinality=0,
    population_entity_path="Atom/(.Header.Context.Role:=Plan)",
    population_unique_constraints=(
        {
            "keys": ("Header.Context.Container.atom", "Header.Context.Plan.Work Sequence Number"),
            "status": "Active",
            "single_value_paths": ("Header.Context.Container.atom", "Header.Context.Plan.Work Sequence Number"),
        },
        {
            "keys": ("Header.Context.Container.scope_unit", "Header.Context.Plan.Work Sequence Number"),
            "status": "Active",
            "single_value_paths": ("Header.Context.Container.scope_unit", "Header.Context.Plan.Work Sequence Number"),
        },
    ),
)
```
