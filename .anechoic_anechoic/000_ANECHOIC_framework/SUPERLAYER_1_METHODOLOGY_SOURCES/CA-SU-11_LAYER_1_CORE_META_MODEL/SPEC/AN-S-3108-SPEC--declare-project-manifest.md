---
identity:
  atom_id: AN-S-3108
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Project Manifest

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Manifest

class ProjectManifest(Manifest):
    pass

declare_entity(
    entity_name='Project Manifest',
    entity_class=ProjectManifest,
    entity_kind='Primary',
)
```
