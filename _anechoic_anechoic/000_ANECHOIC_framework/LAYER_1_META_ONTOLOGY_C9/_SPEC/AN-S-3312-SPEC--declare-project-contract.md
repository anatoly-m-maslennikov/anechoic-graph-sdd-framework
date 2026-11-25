---
atom_family: SPEC
atom_id: AN-S-3312
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Project Contract

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract//Project Contract

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Contract

class ProjectContract(Contract):
    pass

declare_entity(
    entity_name='Project Contract',
    entity_class=ProjectContract,
    entity_kind='Primary',
)
```
