---
atom_family: SPEC
atom_id: AN-S-4899
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.293574+00:00"

---

## Summary

Declare the DES Lens

## Semantics

Groups architecture descriptions, design decisions, interfaces, and their rationale.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/Design Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class DesignLens(Lens):
    node.lens_path = value(fixed='DES')
```
