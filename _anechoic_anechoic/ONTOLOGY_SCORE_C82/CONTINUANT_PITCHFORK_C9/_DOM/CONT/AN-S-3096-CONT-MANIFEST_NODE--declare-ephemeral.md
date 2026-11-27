---
atom_family: SPEC
atom_id: AN-S-3096
concern:
  subject: Ephemeral
  path: Model/Graph/Node
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 7
  updated_at: '2026-11-26T18:38:58.296902+00:00'
---

## Summary

Declare Ephemeral

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node

class Ephemeral(Node):
    node.axes = {'Persistence': 'Ephemeral'}
```
