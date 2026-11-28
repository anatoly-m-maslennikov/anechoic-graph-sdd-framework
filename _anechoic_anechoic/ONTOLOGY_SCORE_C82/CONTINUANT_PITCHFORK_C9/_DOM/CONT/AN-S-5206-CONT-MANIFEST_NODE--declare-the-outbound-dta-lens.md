---
atom_family: SPEC
atom_id: AN-S-5206
concern:
  subject: Outbound DTA
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

Declare the Outbound DTA Lens

## Semantics

Groups transformations from runtime data to the form sent across the
Project boundary.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import OutboundLens

class OutboundDTALens(OutboundLens):
    node.lens_path = value(fixed='IO/OUTBOUND/DTA')
```
