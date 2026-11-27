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
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:02.722238+00:00"
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
