---
identity:
  atom_id: AN-S-3098
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Ticket Atom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Ticket Atom

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class TicketAtom(Atom):
    pass

declare_entity(
    entity_name='Ticket Atom',
    entity_class=TicketAtom,
    entity_kind='Primary',
)
```
