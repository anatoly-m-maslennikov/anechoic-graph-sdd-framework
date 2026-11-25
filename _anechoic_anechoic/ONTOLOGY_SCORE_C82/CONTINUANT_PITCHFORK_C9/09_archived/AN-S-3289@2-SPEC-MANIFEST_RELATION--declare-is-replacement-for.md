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
  version: 2
  updated_at: '2026-11-24T16:58:01.509143+00:00'
---

## Summary

Declare IS_REPLACEMENT_FOR

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_REPLACEMENT_FOR

## Claim

### Prose Claim

The replacement Atom authors this Relation to a different predecessor Atom
by its stable base Atom ID. One replacement can target several predecessors.
A Draft Host proposes replacement. Its links remain after promotion and
predecessor archival. Completed replacement requires an adopted successor
and an Archived predecessor.

## References

AN-S-2733.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Relation

class Relation3289(Relation):
    name = 'IS_REPLACEMENT_FOR'
    source_endpoint = {'level': 'instances', 'entity_paths': (Atom,)}
    target_endpoint = {'level': 'instances', 'entity_paths': (Atom,), 'reference_form': 'base_atom_id'}
```
