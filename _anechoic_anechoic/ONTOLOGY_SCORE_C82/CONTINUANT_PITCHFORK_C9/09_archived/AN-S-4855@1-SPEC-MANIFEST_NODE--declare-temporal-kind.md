---
atom_family: SPEC
atom_id: AN-S-4855
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:03.031041+00:00"
---

## Summary

Declare Temporal Kind

## Claim scope

MODEL//ANECHOIC <+ Graph/Classification//Temporal Kind

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Classification

class TemporalKind(Classification):
    pass
```
