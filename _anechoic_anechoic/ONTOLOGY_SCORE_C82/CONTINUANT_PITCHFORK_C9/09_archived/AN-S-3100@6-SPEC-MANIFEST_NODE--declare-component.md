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
  version: 6
  updated_at: "2026-11-26T14:46:18.757099+00:00"
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

A Component groups its owned Spec Atoms within a responsibility boundary. Its declared hierarchy also governs the corresponding Component Packages. Each non-root Component has exactly one Active Component Manifest.

A folder that represents a child Component ends in an underscore followed by the Component’s stable ID.
