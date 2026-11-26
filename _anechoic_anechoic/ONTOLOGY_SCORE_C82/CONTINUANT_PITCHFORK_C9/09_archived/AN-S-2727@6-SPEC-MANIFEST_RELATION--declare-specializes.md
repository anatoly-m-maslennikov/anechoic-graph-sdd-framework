---
atom_family: SPEC
atom_id: AN-S-2727
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-25T20:47:37.988978+00:00"
---
## Summary

Declare SPECIALIZES

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//SPECIALIZES

## Semantics

The source Atom specializes the Claim of the target Atom.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Relation

class Specializes(Relation):
    name = 'SPECIALIZES'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Atom,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Atom,), 'reference_form': 'base_atom_id'}
    relation.inverse_alias = 'IS_SPECIALIZED_BY'
```
