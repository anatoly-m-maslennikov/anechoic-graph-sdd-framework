---
atom_family: SPEC
atom_id: AN-S-4824
concern:
  subject: Prescribed
  path: Model/Graph/Node//Artifact//SSOT
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 4
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Declare Prescribed

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import SSOT

class Prescribed(SSOT):
    node.axes = {'Perspective': 'To Be'}
```
