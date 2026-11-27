---
atom_family: SPEC
atom_id: AN-S-4907
concern:
  subject: Software Development Lens
  path: Model/Graph/Lens
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T18:00:26.212328+00:00"
---

## Summary

Declare the SWD Lens

## Semantics

Groups engineering rules for implementing and maintaining software.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class SoftwareDevelopmentLens(Lens):
    node.lens_path = value(fixed='SWD')
```
