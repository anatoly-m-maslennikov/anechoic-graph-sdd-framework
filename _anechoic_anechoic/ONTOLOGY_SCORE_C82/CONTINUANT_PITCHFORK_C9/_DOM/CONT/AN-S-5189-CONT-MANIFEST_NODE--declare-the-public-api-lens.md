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
  status: active
  version: 3
  updated_at: "2026-11-28T15:16:37.698017+00:00"
concern:
  subject: Public API
  path: Model/Graph/Lens//SPEC//DES//IO//INBOUND
  relation: is_narrower_than
---

## Summary

Declare the Public API Lens

## Semantics

Groups callable interfaces the Project runtime provides to external
callers. Specify operations, accepted requests, results, and failures.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import InboundLens

class PublicAPILens(InboundLens):
    node.lens_path = value(fixed='IO/INBOUND/PUBLIC_API')
```

## Sources

- AN-S-4896
