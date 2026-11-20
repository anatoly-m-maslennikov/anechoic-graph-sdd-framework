---
identity:
  atom_id: AN-S-2607
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 18
  updated_at: '2026-11-20T16:02:18.721582+00:00'
---

## Summary

Declare Atom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact

class Atom(Artifact):
    pass

declare_entity(
    entity_name='Atom',
    entity_class=Atom,
    entity_kind='Primary',
    identity_properties=('Identity.Atom ID',),
)
```
