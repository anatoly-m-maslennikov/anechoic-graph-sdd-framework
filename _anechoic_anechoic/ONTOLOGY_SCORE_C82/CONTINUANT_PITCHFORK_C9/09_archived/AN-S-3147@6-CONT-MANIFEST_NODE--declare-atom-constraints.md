---
atom_family: SPEC
atom_id: AN-S-3147
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: archived
  version: 6
  updated_at: '2026-11-28T09:21:26.937336+00:00'
---

## Summary

Declare Atom Constraints

## Semantics

Each stable Atom ID has at most one Current revision. An exact Ref ID identifies one revision in its applicable state.

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
    node.constraints.instance_check = check_atom_identity
    node.constraints.instance_relations = {'IS_CONTAINED_BY': {'target_entity_paths': (Component, Atom), 'targets_per_source': 1}}
    node.constraints.population_unique = ({'keys': ('Ref ID',)},)
```
