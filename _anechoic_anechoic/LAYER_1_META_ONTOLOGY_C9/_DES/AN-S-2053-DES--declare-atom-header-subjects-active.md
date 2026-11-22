---
atom_family: SPEC
atom_id: AN-S-2053
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Declare Atom.Header.Subjects.Active

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Main Subject',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Context.Topics',
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
