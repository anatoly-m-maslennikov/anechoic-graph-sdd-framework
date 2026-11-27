---
atom_family: SPEC
atom_id: AN-S-4834
concern:
  subject: Operative Plan
  path: Model/Graph/Node//Ephemeral
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
  updated_at: "2026-11-26T18:39:02.300883+00:00"
---

## Summary

Declare Operative Plan

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Ephemeral

class OperativePlan(Ephemeral):
    node.axes = {'Artifact Kind': 'Ephemeral'}
```
