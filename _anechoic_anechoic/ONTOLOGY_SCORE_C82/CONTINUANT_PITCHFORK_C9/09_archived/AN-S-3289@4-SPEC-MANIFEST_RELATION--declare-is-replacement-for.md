---
atom_family: SPEC
atom_id: AN-S-3289
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T22:59:51.239254+00:00"
---

## Summary

Declare IS_REPLACEMENT_FOR

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_REPLACEMENT_FOR

## Semantics

This Relation records that the successor supersedes a different predecessor Atom's contribution.
One successor can replace several predecessors.

## References

AN-S-2733.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Relation

class Relation3289(Relation):
    name = 'IS_REPLACEMENT_FOR'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Atom,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Atom,), 'reference_form': 'base_atom_id'}
    relation.forbidden_status_pairs = (('active', 'active'),)
```
