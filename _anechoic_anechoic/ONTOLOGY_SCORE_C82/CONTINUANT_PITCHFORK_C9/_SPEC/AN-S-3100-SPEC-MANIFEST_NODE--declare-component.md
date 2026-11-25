---
atom_family: SPEC
atom_id: AN-S-3100
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 3
  updated_at: '2026-11-24T16:58:01.347611+00:00'
---

## Summary

Declare Component

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Structure/Component

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Prescribed

class Component(Prescribed):
    pass
```
