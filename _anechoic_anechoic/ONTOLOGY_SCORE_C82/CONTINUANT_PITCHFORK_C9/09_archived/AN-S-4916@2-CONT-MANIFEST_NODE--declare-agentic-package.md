---
atom_family: SPEC
atom_id: AN-S-4916
concern:
  subject: Agentic Package
  path: Model/Graph/Node//Artifact//SSOT//Realization/Structure/Package
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T17:13:49.285400+00:00"
---

## Summary

Declare Agentic Package

## Semantics

An Agentic Package folder name ends in `__agentic`. Its members are Prompts.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package

class AgenticPackage(Package):
    pass
```
