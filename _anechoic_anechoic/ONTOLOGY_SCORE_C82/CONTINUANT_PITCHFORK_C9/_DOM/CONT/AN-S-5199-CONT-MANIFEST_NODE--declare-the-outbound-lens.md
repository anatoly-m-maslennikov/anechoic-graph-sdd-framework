---
atom_family: SPEC
atom_id: AN-S-5199
concern:
  subject: OUTBOUND
  path: Model/Graph/Lens//SPEC//DES//IO
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

Declare the Outbound Lens

## Semantics

Groups interactions the Project runtime initiates with external systems
and data it sends across its boundary.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import IOLens, ConsumedAPILens, OutboundDTALens

class OutboundLens(IOLens):
    node.lens_path = value(fixed='IO/OUTBOUND')
    node.parts = {
        'CONSUMED_API': ConsumedAPILens,
        'DTA': OutboundDTALens,
    }
```
