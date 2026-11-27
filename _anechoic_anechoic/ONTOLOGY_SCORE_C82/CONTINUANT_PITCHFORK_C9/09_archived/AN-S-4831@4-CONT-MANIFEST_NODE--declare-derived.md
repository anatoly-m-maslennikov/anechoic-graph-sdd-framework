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
  status: "archived"
  version: 4
  updated_at: "2026-11-26T18:39:02.280841+00:00"
---

## Summary

Declare Derived

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Artifact

class Derived(Artifact):
    node.axes = {'Artifact Kind': 'Artifact'}
```
