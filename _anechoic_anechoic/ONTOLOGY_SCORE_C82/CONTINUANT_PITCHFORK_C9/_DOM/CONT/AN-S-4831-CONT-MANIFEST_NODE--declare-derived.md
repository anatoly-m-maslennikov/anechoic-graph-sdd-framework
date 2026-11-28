---
atom_family: SPEC
atom_id: AN-S-4831
concern:
  subject: Derived
  path: Model/Graph/Node//Artifact
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
  updated_at: "2026-11-28T10:28:09.160093+00:00"
---

## Summary

Declare Derived

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Artifact

class Derived(Artifact):
    node.axes = {'Authority': 'Derived'}
```
