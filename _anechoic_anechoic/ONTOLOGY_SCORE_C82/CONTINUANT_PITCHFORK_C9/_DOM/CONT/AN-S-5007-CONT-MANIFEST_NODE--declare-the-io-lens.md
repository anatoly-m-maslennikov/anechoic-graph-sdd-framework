---
atom_family: SPEC
atom_id: AN-S-5007
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 4
  updated_at: "2026-11-28T15:16:37.698017+00:00"
concern:
  subject: IO
  path: Model/Graph/Lens//SPEC//DES
  relation: is_narrower_than
---

## Summary

Declare the IO Lens

## Semantics

Groups interactions across the Project runtime boundary.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import DesignLens, InboundLens, OutboundLens

class IOLens(DesignLens):
    node.lens_path = value(fixed='IO')
    node.parts = {'INBOUND': InboundLens, 'OUTBOUND': OutboundLens}
```

## Sources

- [ISO/IEC/IEEE 29148:2018 — Requirements engineering](https://www.iso.org/standard/72089.html) covers the specification of interface requirements.
