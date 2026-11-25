---
atom_family: SPEC
atom_id: AN-S-3100
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T20:23:21.283934+00:00"
---

## Summary

Declare Component

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Structure/Component

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Prescribed

class Component(Prescribed):
    pass
```

## Semantics

Each non-root Component has exactly one Active Component Manifest.

A folder that represents a child Component ends in an underscore followed by the Component’s stable ID.
