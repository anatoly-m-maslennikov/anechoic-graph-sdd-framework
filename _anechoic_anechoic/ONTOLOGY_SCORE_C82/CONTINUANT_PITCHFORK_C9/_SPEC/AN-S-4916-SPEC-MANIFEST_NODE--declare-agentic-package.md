---
atom_family: SPEC
atom_id: AN-S-4916
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: active
  version: 1
  updated_at: "2026-11-25T19:21:21.408484+00:00"
---

## Summary

Declare Agentic Package

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Realization/Structure/Package//Agentic Package

## Semantics

An Agentic Package folder name ends in `__agentic`. Its members are Prompts.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package

class AgenticPackage(Package):
    pass
```
