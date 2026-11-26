---
atom_family: SPEC
atom_id: AN-S-2134
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T21:03:29.160210+00:00"
---

## Summary

Declare Projection

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//Derived//Projection

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Derived

class Projection(Derived):
    pass
```

## Semantics

A Projection derives a view from source entities. Building, refreshing, or removing the view preserves the identity and authority of those entities. The derivation defines the view independently of its storage. The Projection specification identifies the derivation and configuration for a rebuild.
