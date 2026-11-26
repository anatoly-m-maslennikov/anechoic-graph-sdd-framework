---
atom_family: SPEC
atom_id: AN-S-3362
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T20:33:55.368070+00:00"
---

## Summary

Declare ANSWERS

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//ANSWERS

## Claim

### Prose Claim

A Tier 0 Contract answers a Manifest by accepting a specific responsibility
the Manifest assigns. The Contract states what the Component commits to
deliver and what it requires from callers. The authored Relation points from
the Contract to the Manifest. Derive IS_ANSWERED_BY for the same direct pair.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Contract, Manifest, Relation

class Relation3362(Relation):
    name = 'ANSWERS'
    relation.inverse_alias = 'IS_ANSWERED_BY'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Contract,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Manifest,)}
```
