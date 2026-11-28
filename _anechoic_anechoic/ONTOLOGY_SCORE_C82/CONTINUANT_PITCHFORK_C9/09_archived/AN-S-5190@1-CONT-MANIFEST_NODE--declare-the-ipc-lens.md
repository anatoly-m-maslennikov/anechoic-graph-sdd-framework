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
  status: archived
  version: 1
  updated_at: '2026-11-27T18:25:19.396090+00:00'
concern:
  subject: IPC
  path: Model/Graph/Lens//SPEC//DES//IO//API
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
from anechoic.model import APILens

class IPCLens(APILens):
    node.lens_path = value(fixed='IO/API/IPC')
```
