---
atom_family: SPEC
atom_id: AN-S-3093
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Graph

## Claim scope

MODEL//ANECHOIC <+ Graph

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class Graph:
    pass

declare_entity(
    entity_name='Graph',
    entity_class=Graph,
    entity_kind='Primary',
)
```
