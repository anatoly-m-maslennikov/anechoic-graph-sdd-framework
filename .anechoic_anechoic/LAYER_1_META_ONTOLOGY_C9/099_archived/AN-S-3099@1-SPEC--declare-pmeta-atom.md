---
identity:
  atom_id: AN-S-3099
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare PMETA Atom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//PMETA Atom

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom
from typing import ClassVar

class PMETAAtom(Atom):
    family_marker: ClassVar[str] = "P"

declare_entity(entity_name="PMETA Atom", entity_class=PMETAAtom)
```
