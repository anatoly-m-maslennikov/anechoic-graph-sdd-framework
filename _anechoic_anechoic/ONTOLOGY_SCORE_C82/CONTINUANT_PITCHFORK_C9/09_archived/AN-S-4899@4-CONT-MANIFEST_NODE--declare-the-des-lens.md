---
atom_family: SPEC
atom_id: AN-S-4899
concern:
  subject: DES
  path: Model/Graph/Lens//SPEC
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
  updated_at: "2026-11-26T18:06:59.576811+00:00"
---

## Summary

Declare the DES Lens

## Semantics

Groups architecture descriptions, design decisions, interfaces, and their rationale.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SpecificationLens, IOLens, DomainLens

class DesignLens(SpecificationLens):
    node.lens_path = value(fixed='DES')
    node.parts = {
        'IO': IOLens,
        'DOM': DomainLens,
        '@ONT': DomainLens,
    }
```
