---
atom_family: SPEC
atom_id: AN-S-4813
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

Declare File

## Claim scope

MODEL//ANECHOIC <+ Carrier/File

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Carrier

class File(Carrier):
    pass
```
