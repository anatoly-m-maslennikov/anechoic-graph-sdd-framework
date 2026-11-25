---
atom_family: SPEC
atom_id: AN-S-2060
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T19:32:44.501800+00:00"
---

## Summary

Declare Atom.Header.Container.atom

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='atom',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Context.Container',
    value_format='atom_id',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
)
```
