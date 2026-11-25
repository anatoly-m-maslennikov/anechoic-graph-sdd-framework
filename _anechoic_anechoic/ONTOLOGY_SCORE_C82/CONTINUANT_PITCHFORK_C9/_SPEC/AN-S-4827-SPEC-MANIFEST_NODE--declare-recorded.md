---
atom_family: SPEC
atom_id: AN-S-4827
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Declare Recorded

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Recorded

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import SSOT

class Recorded(SSOT):
    pass
```
