---
atom_family: SPEC
atom_id: AN-S-3105
concern:
  subject: SSOT
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
  version: 7
  updated_at: "2026-11-26T18:39:02.273635+00:00"
---

## Summary

Declare SSOT

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Artifact

class SSOT(Artifact):
    node.axes = {'Artifact Kind': 'Artifact'}
```

## Semantics

An SSOT Artifact is the authoritative source for the facts it carries. Each fact has one authoritative source within its applicable context. A derived representation preserves that source binding.
