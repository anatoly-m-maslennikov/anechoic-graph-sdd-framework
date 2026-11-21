---
atom_family: SPEC
atom_id: AN-S-3115
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Package Spec

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Package Spec

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class PackageSpec(SpecAtom):
    pass

declare_entity(
    entity_name='Package Spec',
    entity_class=PackageSpec,
    entity_kind='Primary',
)
```
