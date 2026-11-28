---
atom_family: SPEC
atom_id: AN-S-5189
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: archived
  version: 2
  updated_at: "2026-11-27T18:25:19.395007+00:00"
concern:
  subject: API
  path: Model/Graph/Lens//SPEC//DES//IO
  relation: is_narrower_than
---

## Summary

Declare the API Lens

## Semantics

Groups programmatic interface contracts. Specify the operations a caller can
invoke, the accepted inputs, and the results or failures. This scope includes
CLI, REST API, DTA, MCP, and IPC interfaces.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import IOLens, IPCLens

class APILens(IOLens):
    node.lens_path = value(fixed='IO/API')
    node.parts = {'IPC': IPCLens}
```

## Sources

- AN-S-4896
