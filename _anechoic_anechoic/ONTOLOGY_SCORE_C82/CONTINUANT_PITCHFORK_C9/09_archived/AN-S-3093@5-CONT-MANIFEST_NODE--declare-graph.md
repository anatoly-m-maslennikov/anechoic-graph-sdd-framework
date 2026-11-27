---
atom_family: SPEC
atom_id: AN-S-3093
concern:
  subject: Graph
  path: Model
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T16:50:19.107019+00:00"
---

## Summary

Declare Graph

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

class Graph:
    pass
```

## Semantics

The Model declares the kinds, Properties, and admissible Relations. Project Structure records the actual Components and Packages and their declared hierarchy. A change to one Project’s structure preserves the Model meaning of its kinds and Relations.
