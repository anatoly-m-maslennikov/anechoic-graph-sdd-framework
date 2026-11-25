---
atom_family: SPEC
atom_id: AN-S-3323
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T20:33:55.142282+00:00"
---

## Summary

Declare IS_SOLUTION_FOR

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//IS_SOLUTION_FOR

## Claim

### Prose Claim

A Tier 1 SPEC Atom is a solution for a Tier 0 Contract when its claim
describes how to meet a specific guarantee in that Contract. Any Tier 1
SPEC Template can play this role. The authored Relation points from the
Tier 1 Atom to the Contract. Derive HAS_SOLUTION for the same direct
pair. The tier and guarantee rules are authoring rules.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Contract, Relation, SpecAtom

class Relation3323(Relation):
    name = 'IS_SOLUTION_FOR'
    relation.inverse_alias = 'HAS_SOLUTION'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (SpecAtom,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Contract,)}
```
