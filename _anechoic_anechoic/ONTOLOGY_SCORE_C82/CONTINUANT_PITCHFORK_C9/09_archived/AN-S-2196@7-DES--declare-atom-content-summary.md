---
atom_family: SPEC
atom_id: AN-S-2196
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-25T20:40:57.356204+00:00"
---
## Summary

Declare Atom.Content.Summary

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Summary", relation_name="IS_PROPERTY_OF", base_path="Atom.Content",
    property_occurrence_cardinality=1, value_cardinality=1, dependent_property_cardinality=0,
    population_entity_path="Atom",
    population_functional_dependencies=(
        {"keys": ("Header.Identity.ID",), "dependents": ("Content.Summary",),
         "status_groups": ("Current", "Backlog", "Archived")},
    ),
)
```

