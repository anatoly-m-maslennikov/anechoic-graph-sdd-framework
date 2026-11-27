---
atom_family: SPEC
atom_id: AN-S-5006
container:
  component: C9
concern:
  subject: Operator
  path: Model/Graph/Node//Actor
  relation: is_narrower_than
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 1
  updated_at: '2026-11-26T17:41:09.848566+00:00'
---

## Summary

Declare Operator

## Semantics

An Operator is a human Actor who directs Project work.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(Operator, Actor)
```
