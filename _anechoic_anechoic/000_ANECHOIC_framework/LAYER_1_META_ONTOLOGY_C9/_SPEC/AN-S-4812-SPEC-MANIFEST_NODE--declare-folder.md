---
atom_family: SPEC
atom_id: AN-S-4812
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T19:40:36.199163+00:00"
---

## Summary

Declare Folder

## Claim scope

MODEL//ANECHOIC <+ Carrier/Folder

## Semantics

A Folder represents an entity through a directory assigned to that entity.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Carrier

class Folder(Carrier):
    pass
```
