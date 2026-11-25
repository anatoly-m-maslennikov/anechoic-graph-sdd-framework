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
  status: "active"
  version: 4
  updated_at: "2026-11-25T20:33:55.439357+00:00"
---

## Summary

Declare ANSWERS

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//ANSWERS

## Semantics

The Contract takes on a responsibility assigned by the Component Manifest.
It states what the Component delivers and what it requires from callers.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Contract, Relation

class Relation3362(Relation):
    name = 'ANSWERS'
    relation.inverse_alias = 'IS_ANSWERED_BY'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Contract,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (ComponentManifest,)}
```
