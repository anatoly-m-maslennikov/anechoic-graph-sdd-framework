---
atom_family: SPEC
atom_id: AN-S-4940
concern:
  subject: CONTINUANT
  path: Model/Graph/Lens//SPEC//DES//DOM
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
  updated_at: "2026-11-26T18:34:34.858975+00:00"
---
## Summary

Declare the DOM/CONT Lens

## Semantics

Describes the Domain’s entities, properties, relations, and invariants.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import DomainLens

class ContinuantLens(DomainLens):
    node.lens_path = value(fixed='DOM/CONT')
    node.control_flow = value(fixed='Declarative')
```

## Sources

- [ISO/IEC 21838-2:2021 — Basic Formal Ontology](https://www.iso.org/standard/74572.html) supplies the Continuant terminology.
