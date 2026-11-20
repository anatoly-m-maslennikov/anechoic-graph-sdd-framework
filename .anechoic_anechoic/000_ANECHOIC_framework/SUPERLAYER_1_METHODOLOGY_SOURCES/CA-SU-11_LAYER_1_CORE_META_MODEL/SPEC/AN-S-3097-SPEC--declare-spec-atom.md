---
identity:
  atom_id: AN-S-3097
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Spec Atom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom
from typing import ClassVar

class SpecAtom(Atom):
    family_marker: ClassVar[str] = "S"

declare_entity(entity_name="Spec Atom", entity_class=SpecAtom)
```
