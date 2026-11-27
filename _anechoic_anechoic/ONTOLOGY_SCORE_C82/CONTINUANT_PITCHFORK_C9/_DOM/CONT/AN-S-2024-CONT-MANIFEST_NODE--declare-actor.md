---
atom_family: SPEC
atom_id: AN-S-2024
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 6
  updated_at: '2026-11-26T18:38:58.296902+00:00'
concern:
  subject: Actor
  path: Model/Graph/Node
  relation: is_narrower_than
---

## Summary

Declare Actor

## Semantics

An Actor participates in Project work.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node

class Actor(Node):
    node.axes = {'Temporality': 'Continuant'}
```
