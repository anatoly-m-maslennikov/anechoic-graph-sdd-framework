---
atom_family: SPEC
atom_id: AN-S-3096
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 3
  updated_at: '2026-11-24T16:58:01.339044+00:00'
---

## Summary

Declare Ephemeral

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Ephemeral

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node

class Ephemeral(Node):
    pass
```
