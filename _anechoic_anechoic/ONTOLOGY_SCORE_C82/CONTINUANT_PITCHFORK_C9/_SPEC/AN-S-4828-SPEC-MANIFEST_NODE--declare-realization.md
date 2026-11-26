---
atom_family: SPEC
atom_id: AN-S-4828
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T22:52:51.365116+00:00"
---

## Summary

Declare Realization

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Realization

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import SSOT

class Realization(SSOT):
    pass
```

## Semantics

Realization records what exists and how it behaves. Its files and declarations supply evidence for observed interfaces and dependencies. A derived view preserves the identity of those sources.
