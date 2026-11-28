---
atom_family: SPEC
atom_id: AN-S-5200
concern:
  subject: Consumed API
  path: Model/Graph/Lens//SPEC//DES//IO//OUTBOUND
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 1
  updated_at: "2026-11-28T15:16:37.698017+00:00"
---

## Summary

Declare the Consumed API Lens

## Semantics

Groups external callable interfaces the Project runtime uses. Specify
the required operations, outcomes, and failure behavior.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import OutboundLens

class ConsumedAPILens(OutboundLens):
    node.lens_path = value(fixed='IO/OUTBOUND/CONSUMED_API')
```
