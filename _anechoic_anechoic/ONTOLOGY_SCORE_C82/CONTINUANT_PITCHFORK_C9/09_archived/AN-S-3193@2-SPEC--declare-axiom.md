---
atom_family: SPEC
atom_id: AN-S-3193
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 2
  updated_at: '2026-11-21T21:19:38+00:00'
---

## Summary

Declare Axiom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Axiom

## Claim

### Prose Claim

The Model defines Axiom as an Atom Template for the SPEC Lens. An Axiom
states an accepted premise for the level 0 Project and uses Tier -1.
Its Carrier uses the Project root and its lifecycle status directories.

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
