---
atom_family: SPEC
atom_id: AN-S-3115
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 4
  updated_at: '2026-11-22T08:56:40.513203+00:00'
---

## Summary

Declare Component Seed Manifest

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Component Seed Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class ComponentSeedManifest(SpecAtom):
    pass

declare_entity(
    entity_name='Component Seed Manifest',
    entity_class=ComponentSeedManifest,
    entity_kind='Primary',
)
```
