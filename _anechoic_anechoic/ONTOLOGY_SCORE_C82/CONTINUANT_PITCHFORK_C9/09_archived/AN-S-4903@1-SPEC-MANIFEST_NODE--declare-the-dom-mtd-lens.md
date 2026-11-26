---
atom_family: SPEC
atom_id: AN-S-4903
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T12:40:53.325324+00:00"
relations:
  IS_REFERENCE:
  - AN-T-3922@1
---

## Summary

Declare the DOM/MTD Lens

## Semantics

Defines actions, workflows, and the conditions that govern their execution in a Domain.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/Domain Lens/Methodology Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class MethodologyLens(Lens):
    lens_path = value(fixed='DOM/MTD')
    control_flow = value(fixed='Imperative')
```
