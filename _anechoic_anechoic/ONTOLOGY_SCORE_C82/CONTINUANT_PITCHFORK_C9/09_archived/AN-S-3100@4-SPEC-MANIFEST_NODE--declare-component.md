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
  version: 4
  updated_at: "2026-11-25T17:50:12.063132+00:00"
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

A folder that represents a child Component ends in an underscore followed by the Component’s stable ID.
