---
atom_family: SPEC
atom_id: AN-S-4903
concern:
  subject: OCCURRENT
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
  version: 5
  updated_at: "2026-11-26T18:34:34.852924+00:00"
---

## Summary

Declare the OCCURRENT Lens

## Semantics

Describes the actions, workflows, and conditions that govern their execution in a Domain.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import DomainLens

class OccurrentLens(DomainLens):
    node.lens_path = value(fixed='DOM/MTD')
    node.control_flow = value(fixed='Imperative')
```

## Sources

- [ISO/IEC 21838-2:2021 — Basic Formal Ontology](https://www.iso.org/standard/74572.html) supplies the Occurrent terminology.
- [ISO/IEC 24744:2014 — Metamodel for development methodologies](https://www.iso.org/standard/62644.html) informs the modeling of methods and work.
