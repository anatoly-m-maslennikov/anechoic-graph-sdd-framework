---
atom_family: SPEC
atom_id: AN-S-4907
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.432594+00:00"

---

## Summary

Declare the SWD Lens

## Semantics

Groups engineering rules for implementing and maintaining software.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/Software Development Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class SoftwareDevelopmentLens(Lens):
    node.lens_path = value(fixed='SWD')
```
