---
atom_family: SPEC
atom_id: AN-S-2709
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 8
  updated_at: '2026-11-12T21:29:33.223207+00:00'
---
## Summary

Define Relation Meaning

## Claim

### Prose Claim


Relation Meaning is the canonical meaning of a reusable Relation Type.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Meaning",
    relation_name="IS_PROPERTY_OF",
    base_path="Relation",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
