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
  status: active
  version: 6
  updated_at: '2026-11-26T18:18:17.043477+00:00'
---

## Summary

Declare the DOM Lens

## Semantics

Covers the structure and behavior of the Domain addressed by a Specification.

`DOM = OCCURRENT + CONTINUANT`.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import DesignLens, ContinuantLens, OccurrentLens

class DomainLens(DesignLens):
    node.lens_path = value(fixed='DOM')
    node.aliases = ('ONT',)
    node.parts = {
        'CONTINUANT': ContinuantLens,
        'OCCURRENT': OccurrentLens,
    }
```

## Sources

- [ISO/IEC 21838-1:2021 — Requirements for top-level ontologies](https://www.iso.org/standard/71954.html) addresses their relationship to domain ontologies.
