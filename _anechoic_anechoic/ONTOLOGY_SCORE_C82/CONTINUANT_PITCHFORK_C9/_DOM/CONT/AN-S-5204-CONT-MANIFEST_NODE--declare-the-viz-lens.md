---
atom_family: SPEC
atom_id: AN-S-5204
concern:
  subject: VIZ
  path: Model/Graph/Lens//SPEC//DES//IO//INBOUND//UI
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

Declare the VIZ Lens

## Semantics

Groups the visual presentation of information through the UI.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import UILens

class VIZLens(UILens):
    node.lens_path = value(fixed='IO/INBOUND/UI/VIZ')
```
