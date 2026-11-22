---
atom_family: SPEC
atom_id: AN-S-3110
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

Declare Purpose

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class Purpose(SpecAtom):
    pass

declare_entity(
    entity_name='Purpose',
    entity_class=Purpose,
    entity_kind='Primary',
)
```
