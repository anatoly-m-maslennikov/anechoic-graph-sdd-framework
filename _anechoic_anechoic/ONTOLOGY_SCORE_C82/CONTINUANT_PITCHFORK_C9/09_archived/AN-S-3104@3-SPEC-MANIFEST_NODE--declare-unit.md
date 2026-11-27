---
atom_family: SPEC
atom_id: AN-S-3104
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T14:46:18.787277+00:00"
---

## Summary

Declare Unit

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Realization/Content/Module/Unit

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Realization

class Unit(Realization):
    pass
```
