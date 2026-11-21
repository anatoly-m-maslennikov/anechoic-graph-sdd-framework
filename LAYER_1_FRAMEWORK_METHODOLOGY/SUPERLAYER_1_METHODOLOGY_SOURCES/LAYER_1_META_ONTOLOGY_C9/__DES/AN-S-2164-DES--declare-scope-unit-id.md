---
atom_family: SPEC
atom_id: AN-S-2164
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-12T22:08:11.294473+00:00'
---

## Summary

Declare Scope Unit ID

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="ID",
    relation_name="IS_PROPERTY_OF",
    base_path="Scope Unit",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

## Semantics

Every Scope Unit has a stable ID. A non-root Scope Unit keeps its ID through moves and renames; the ID distinguishes those operations from removal. `CA-SU--1` identifies the predefined Scope Unit named `world`.
