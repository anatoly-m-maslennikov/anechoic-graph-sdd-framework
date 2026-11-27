---
atom_family: SPEC
atom_id: AN-S-5004
concern:
  subject: Solution
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 2
  updated_at: '2026-11-26T17:13:39.181253+00:00'
---

## Summary

Declare Solution

## Semantics

A Solution describes how its Component satisfies the public Contract in its
Manifest. A delegated Action uses the child Manifest’s public Contract. The
child Solution describes how the child satisfies that Contract.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(Solution, SpecAtom)
```
