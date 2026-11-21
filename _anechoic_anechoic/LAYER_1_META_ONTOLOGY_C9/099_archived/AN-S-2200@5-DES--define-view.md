---
atom_family: SPEC
atom_id: AN-S-2200
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: '2026-11-13T04:14:36.994022+00:00'
---
## Summary

Define View

## Claim

### Prose Claim

A View is a Workbench SQL document in one Workspace. It has one stable string ID, one complete SQL query and may have one name. A View can be edited, run, fetched, focused, renamed, removed or saved through the Workspace operations.

### Formal Claim

```python
from dataclasses import dataclass, field
from anechoic.formal_claims import Cardinality, declare_entity

@dataclass
class View:
    id: str = field(metadata={
        "property_occurrence_cardinality": 1,
        "value_cardinality": 1,
    })
    sql: str = field(metadata={
        "property_occurrence_cardinality": 1,
        "value_cardinality": 1,
    })
    name: str = field(metadata={
        "property_occurrence_cardinality": Cardinality(minimum=0, maximum=1),
        "value_cardinality": Cardinality(minimum=0, maximum=1),
    })

declare_entity(entity_name="View", entity_class=View)
```
