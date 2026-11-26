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
  status: "active"
  version: 1
  updated_at: '2026-11-24T19:18:53+00:00'
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
