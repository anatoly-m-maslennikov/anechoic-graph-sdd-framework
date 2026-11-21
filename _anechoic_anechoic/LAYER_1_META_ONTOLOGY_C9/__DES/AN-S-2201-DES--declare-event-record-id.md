---
atom_family: SPEC
atom_id: AN-S-2201
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-13T04:32:46.823926+00:00'
---
## Summary

Declare Event Record.ID

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="ID",
    relation_name="IS_PROPERTY_OF",
    base_path="Event Record",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
    population_unique_constraints=({"keys": ("ID",)},),
)
```
