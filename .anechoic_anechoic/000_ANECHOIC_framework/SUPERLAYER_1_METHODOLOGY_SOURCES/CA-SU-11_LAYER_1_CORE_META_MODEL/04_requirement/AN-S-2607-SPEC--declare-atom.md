---
identity:
  atom_id: AN-S-2607
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 16
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Atom

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact
from dataclasses import field
from typing import ClassVar

class Atom(Artifact):
    atom_id: str
    version: int = field(metadata={"minimum_value": 1})
    ref_id: str
    family_marker: ClassVar[str | None] = None

def check_atom_identity(atom: Atom) -> bool:
    parts = atom.atom_id.split("-")
    if len(parts) != 3:
        return False
    prefix, family, number = parts
    if not (prefix.isascii() and prefix.isalpha() and prefix.isupper()
            and family == atom.family_marker and number.isascii() and number.isdecimal()):
        return False
    revision = f"{atom.atom_id}@{atom.version}"
    return atom.ref_id in (revision, f"{revision}-draft")

declare_entity(
    entity_name="Atom",
    entity_class=Atom,
    instance_check=check_atom_identity,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component", "Node//Artifact//Atom"), "targets_per_source": 1},
    },
    population_unique_constraints=({"keys": ("Ref ID",)},),
)
```
