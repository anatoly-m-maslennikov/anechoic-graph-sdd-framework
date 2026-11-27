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
  version: 4
  updated_at: "2026-11-26T18:18:20.882679+00:00"
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
