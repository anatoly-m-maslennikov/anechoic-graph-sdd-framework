---
atom_family: SPEC
atom_id: AN-S-3362
concern:
  subject: ANSWERS
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:34.733608+00:00"
---

## Summary

Declare ANSWERS

## Semantics

A Component Solution answers its Component Manifest. It describes how the
Component satisfies the public Contract in that Manifest.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Relation, Solution

class Relation3362(Relation):
    name = 'ANSWERS'
    relation.inverse_alias = 'IS_ANSWERED_BY'
    relation.endpoint_pairs = (
        {'source_endpoint': {'level': 'instances', 'entity_paths': (Solution,)},
         'target_endpoint': {'level': 'instances', 'entity_paths': (ComponentManifest,)}},
    )
```
