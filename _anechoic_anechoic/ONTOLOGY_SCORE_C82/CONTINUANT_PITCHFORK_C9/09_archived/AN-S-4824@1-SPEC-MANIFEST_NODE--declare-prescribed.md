---
atom_family: SPEC
atom_id: AN-S-4824
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:02.816493+00:00"
---

## Summary

Declare Prescribed

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import SSOT

class Prescribed(SSOT):
    pass
```
