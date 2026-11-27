---
atom_family: SPEC
atom_id: AN-S-3289
concern:
  subject: IS_REPLACEMENT_FOR
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-26T16:34:52.393856+00:00"
---

## Summary

Declare IS_REPLACEMENT_FOR

## Semantics

This Relation records that the successor supersedes a different predecessor Atom's contribution.
One successor can replace several predecessors.

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
