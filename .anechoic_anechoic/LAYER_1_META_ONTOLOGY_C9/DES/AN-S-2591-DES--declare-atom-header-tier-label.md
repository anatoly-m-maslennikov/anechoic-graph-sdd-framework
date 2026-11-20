---
identity:
  atom_id: AN-S-2591
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-13T22:53:30.315950+00:00'
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

