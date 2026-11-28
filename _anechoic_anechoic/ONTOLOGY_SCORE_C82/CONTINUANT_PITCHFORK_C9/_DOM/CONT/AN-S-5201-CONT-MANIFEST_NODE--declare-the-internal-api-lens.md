---
atom_family: SPEC
atom_id: AN-S-5201
concern:
  subject: Internal API
  path: Model/Graph/Lens//SPEC//SWE//SWD
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

Declare the Internal API Lens

## Semantics

Groups callable interfaces between Components inside the Project runtime.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SoftwareDevelopmentLens, IPCLens

class InternalAPILens(SoftwareDevelopmentLens):
    node.lens_path = value(fixed='SWD/INTERNAL_API')
    node.parts = {
        'IPC': IPCLens,
    }
```
