---
atom_family: SPEC
atom_id: AN-S-2607
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 21
  updated_at: "2026-11-25T16:00:37.691613+00:00"
---

## Summary

Declare Atom

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Prescribed

class Atom(Prescribed):
    node.identity = header.atom_id
```
