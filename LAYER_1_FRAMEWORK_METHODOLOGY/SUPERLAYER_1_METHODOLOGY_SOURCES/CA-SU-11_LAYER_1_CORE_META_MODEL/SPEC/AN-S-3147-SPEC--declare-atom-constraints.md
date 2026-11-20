---
identity:
  atom_id: AN-S-3147
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Atom Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

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
    entity_name='Atom Constraints',
    constraints_for='Node//Artifact//Atom',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component', 'Node//Artifact//Atom'), 'targets_per_source': 1}},
    population_unique_constraints=({'keys': ('Ref ID',)},),
    instance_check=check_atom_identity,
)
```
