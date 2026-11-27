---
atom_family: SPEC
atom_id: AN-S-2998
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 2
  updated_at: '2026-11-26T17:41:09.846576+00:00'
concern:
  subject: AI Agent
  path: Model/Graph/Node//Actor
  relation: is_narrower_than
---

## Summary

Declare AI Agent

## Semantics

An AI Agent is an Actor that performs delegated work using an AI model.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(AIAgent, Actor)
```
