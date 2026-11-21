---
atom_family: SPEC
atom_id: AN-S-2125
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: '2026-11-12T19:06:42.090680+00:00'
---
## Summary

Declare Atom.Header.Status

## Claim

### Prose Claim

A Status with a dedicated folder has one integer Status Order Number from 0 through 999. Order numbers are distinct across Status values. Declare each number once, including for a Status admitted by several Roles. Active uses its Container's base directory.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Status",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.State",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
    allowed_values=("Draft", "Active", "Archived"),
    status_order_numbers={"Draft": 0, "Archived": 99},
)
```
