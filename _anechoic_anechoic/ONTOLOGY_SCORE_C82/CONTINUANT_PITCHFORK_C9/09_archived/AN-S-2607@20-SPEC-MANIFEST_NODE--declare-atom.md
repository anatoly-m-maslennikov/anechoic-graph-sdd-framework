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
  status: "archived"
  version: 20
  updated_at: '2026-11-24T16:58:01.315744+00:00'
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
    identity = header.atom_id
```
