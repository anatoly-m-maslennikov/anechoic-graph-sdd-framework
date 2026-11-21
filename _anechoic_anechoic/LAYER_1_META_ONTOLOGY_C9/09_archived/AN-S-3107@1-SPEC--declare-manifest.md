---
atom_family: SPEC
atom_id: AN-S-3107
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
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
from typing import ClassVar
from dataclasses import field

class Manifest(SpecAtom):
    control_flow: ClassVar[str] = "Declarative"
    lens_whitelist: list[str] | None = field(default=None, kw_only=True)

declare_entity(
    entity_name="Manifest",
    entity_class=Manifest,
)
```
