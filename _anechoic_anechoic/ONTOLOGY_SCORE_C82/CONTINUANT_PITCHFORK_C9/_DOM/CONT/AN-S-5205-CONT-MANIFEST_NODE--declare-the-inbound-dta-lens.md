---
atom_family: SPEC
atom_id: AN-S-5205
concern:
  subject: Inbound DTA
  path: Model/Graph/Lens//SPEC//DES//IO//INBOUND
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

Declare the Inbound DTA Lens

## Semantics

Groups transformations from externally received data to the runtime data
model at the Project boundary.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import InboundLens

class InboundDTALens(InboundLens):
    node.lens_path = value(fixed='IO/INBOUND/DTA')
```
