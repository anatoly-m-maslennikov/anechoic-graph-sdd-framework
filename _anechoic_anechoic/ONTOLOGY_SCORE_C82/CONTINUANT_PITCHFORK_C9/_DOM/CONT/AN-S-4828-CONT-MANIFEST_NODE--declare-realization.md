---
atom_family: SPEC
atom_id: AN-S-4828
concern:
  subject: Realization
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
  version: 5
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Declare Realization

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import SSOT

class Realization(SSOT):
    node.axes = {'Perspective': 'As Is'}
```

## Semantics

Realization records what exists and how it behaves. Its files and declarations supply evidence for observed interfaces and dependencies. A derived view preserves the identity of those sources.
