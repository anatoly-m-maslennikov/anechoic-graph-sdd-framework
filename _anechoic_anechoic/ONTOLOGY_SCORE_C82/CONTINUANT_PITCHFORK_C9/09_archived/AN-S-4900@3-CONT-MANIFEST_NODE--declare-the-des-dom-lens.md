---
atom_family: SPEC
atom_id: AN-S-4900
concern:
  subject: Design Domain Lens
  path: Model/Graph/Lens/Design Lens
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
  updated_at: "2026-11-26T18:00:26.225315+00:00"
---

## Summary

Declare the DES/DOM Lens

## Semantics

Groups domain workflows, actions, and steps specified as part of a design.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class DesignDomainLens(Lens):
    node.lens_path = value(fixed='DES/DOM')
```
