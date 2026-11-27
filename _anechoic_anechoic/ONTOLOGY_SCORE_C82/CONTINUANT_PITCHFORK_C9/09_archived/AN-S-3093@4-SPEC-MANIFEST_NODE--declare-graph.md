---
atom_family: SPEC
atom_id: AN-S-3093
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.010604+00:00"
---

## Summary

Declare Graph

## Claim scope

MODEL//ANECHOIC <+ Graph

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

class Graph:
    pass
```

## Semantics

The Model declares the kinds, Properties, and admissible Relations. Project Structure records the actual Components and Packages and their declared hierarchy. A change to one Project’s structure preserves the Model meaning of its kinds and Relations.
