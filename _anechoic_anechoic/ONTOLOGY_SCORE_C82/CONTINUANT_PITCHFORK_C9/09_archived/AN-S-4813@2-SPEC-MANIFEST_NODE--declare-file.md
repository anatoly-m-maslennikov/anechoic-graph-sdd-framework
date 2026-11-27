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
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:02.731641+00:00"
---

## Summary

Declare File

## Claim scope

MODEL//ANECHOIC <+ Carrier/File

## Semantics

A File represents content carried as bytes at a filesystem path.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Carrier

class File(Carrier):
    pass
```
