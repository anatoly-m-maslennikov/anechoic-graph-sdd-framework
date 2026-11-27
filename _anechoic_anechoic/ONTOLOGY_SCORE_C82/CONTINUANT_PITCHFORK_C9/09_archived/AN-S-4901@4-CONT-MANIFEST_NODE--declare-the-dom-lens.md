---
atom_family: SPEC
atom_id: AN-S-4901
concern:
  subject: DOM
  path: Model/Graph/Lens//SPEC//DES
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T18:06:59.586215+00:00"
---

## Summary

Declare the DOM Lens

## Semantics

Groups the structure and behavior that characterize a Domain.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import DesignLens, ContinuantLens, OccurrentLens

class DomainLens(DesignLens):
    node.lens_path = value(fixed='DOM')
    node.parts = {
        'CONTINUANT': ContinuantLens,
        'OCCURRENT': OccurrentLens,
    }
```
