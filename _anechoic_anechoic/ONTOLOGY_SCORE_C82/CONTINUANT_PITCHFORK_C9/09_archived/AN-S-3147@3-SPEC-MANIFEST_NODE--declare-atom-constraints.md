---
atom_family: SPEC
atom_id: AN-S-3147
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T23:18:33.190860+00:00'
---

## Summary

Declare Atom Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Component, NodeConstraints

def check_atom_identity(atom: Atom) -> bool:
    parts = atom.atom_id.split("-")
    if len(parts) != 3:
        return False
    prefix, family, number = parts
    if not (prefix.isascii() and prefix.isalpha() and prefix.isupper()
            and (family == atom.family_marker or (atom.family_marker == 'C' and family == 'P'))
            and number.isascii() and number.isdecimal()):
        return False
    revision = f"{atom.atom_id}@{atom.version}"
    return atom.ref_id in (revision, f"{revision}-draft")

class Constraints(NodeConstraints):
    bearer = Atom
    instance_check = check_atom_identity
    instance_relation_constraints = {'IS_CONTAINED_BY': {'target_entity_paths': (Component, Atom), 'targets_per_source': 1}}
    population_unique_constraints = ({'keys': ('Ref ID',)},)
```
