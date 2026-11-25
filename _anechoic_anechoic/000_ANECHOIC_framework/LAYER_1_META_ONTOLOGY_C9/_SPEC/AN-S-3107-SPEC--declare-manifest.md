---
atom_family: SPEC
atom_id: AN-S-3107
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

Declare Manifest

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class Manifest(SpecAtom):
    pass

declare_entity(
    entity_name='Manifest',
    entity_class=Manifest,
    entity_kind='Primary',
)
```
