---
atom_family: SPEC
atom_id: AN-S-5190
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 2
  updated_at: "2026-11-28T15:16:37.698017+00:00"
concern:
  subject: IPC
  path: Model/Graph/Lens//SPEC//SWE//SWD//Internal API
  relation: is_narrower_than
---

## Summary

Declare the IPC Lens

## Semantics

Groups callable contracts between processes on the same host. Specify the
accepted requests, responses, and failure behavior of private peers. Declare
the transport and wire protocol in the owning Component Manifest.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import InternalAPILens

class IPCLens(InternalAPILens):
    node.lens_path = value(fixed='SWD/INTERNAL_API/IPC')
```
