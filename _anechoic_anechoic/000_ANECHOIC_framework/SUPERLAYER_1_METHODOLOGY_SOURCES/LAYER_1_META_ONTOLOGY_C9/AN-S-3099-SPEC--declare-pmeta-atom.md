---
atom_family: SPEC
atom_id: AN-S-3099
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare PMETA Atom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//PMETA Atom

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class PMETAAtom(Atom):
    pass

declare_entity(
    entity_name='PMETA Atom',
    entity_class=PMETAAtom,
    entity_kind='Primary',
)
```
