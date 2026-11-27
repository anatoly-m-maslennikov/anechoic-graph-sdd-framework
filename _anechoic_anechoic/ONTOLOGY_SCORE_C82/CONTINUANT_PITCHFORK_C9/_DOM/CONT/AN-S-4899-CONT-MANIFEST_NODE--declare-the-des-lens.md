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
  status: active
  version: 6
  updated_at: '2026-11-26T18:18:17.040838+00:00'
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
    }
```

## Sources

- [ISO/IEC/IEEE 42010:2022 — Architecture description](https://www.iso.org/standard/74393.html)
- [The Open Group — TOGAF Standard, 10th Edition](https://help.opengroup.org/hc/en-us/articles/32726995273362-Understanding-the-TOGAF-Standard) describes architecture content and method.
