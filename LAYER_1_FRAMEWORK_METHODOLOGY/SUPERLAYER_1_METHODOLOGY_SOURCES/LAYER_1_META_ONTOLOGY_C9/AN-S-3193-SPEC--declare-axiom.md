---
atom_family: SPEC
atom_id: AN-S-3193
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-21T18:17:21+00:00'
---

## Summary

Declare Axiom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Axiom

## Claim

### Prose Claim

The Axiom Template states an accepted premise for the Project.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class Axiom(SpecAtom):
    pass

declare_entity(
    entity_name='Axiom',
    entity_class=Axiom,
    entity_kind='Primary',
)
```
