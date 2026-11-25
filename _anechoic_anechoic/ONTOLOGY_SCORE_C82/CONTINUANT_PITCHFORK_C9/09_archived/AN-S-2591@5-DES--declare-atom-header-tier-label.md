---
atom_family: SPEC
atom_id: AN-S-2591
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T19:32:45.609759+00:00"
---
## Summary

Declare Atom.Header.Tier.Label

## Claim

### Prose Claim

When a Tier Label is present, Tier 1 requires Core, Tier 2 requires General, Tier 3 requires Standard, and Tier 4 requires Detail.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Label',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.Context.Tier',
    value_format=str, value_cardinality=Cardinality(minimum=0, maximum=1), dependent_property_cardinality=0,
)
```

