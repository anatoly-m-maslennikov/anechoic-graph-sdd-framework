---
atom_family: SPEC
atom_id: AN-S-2606
concern:
  subject: Node
  path: Model/Graph
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 16
  updated_at: "2026-11-28T10:28:09.160093+00:00"
---

## Summary

Declare Node

## Semantics

Each Node axis has its own Manifest on Node. A subtype inherits its parent's axis values. An explicit assignment overrides the inherited value for that subtype and its descendants.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

class Node:
    node.axes = {'Independency': 'Primary Entity'}
```
