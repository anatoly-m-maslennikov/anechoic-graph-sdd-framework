---
atom_family: SPEC
atom_id: AN-S-3095
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.034746+00:00"
---

## Summary

Declare Artifact

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node

class Artifact(Node):
    pass
```
