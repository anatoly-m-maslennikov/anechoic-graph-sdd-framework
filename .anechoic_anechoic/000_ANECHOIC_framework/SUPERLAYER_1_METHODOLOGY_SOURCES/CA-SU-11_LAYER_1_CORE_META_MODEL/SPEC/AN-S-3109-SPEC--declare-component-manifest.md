---
identity:
  atom_id: AN-S-3109
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Component Manifest

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Component Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Manifest

class ComponentManifest(Manifest):
    pass

declare_entity(
    entity_name='Component Manifest',
    entity_class=ComponentManifest,
    entity_kind='Primary',
)
```
