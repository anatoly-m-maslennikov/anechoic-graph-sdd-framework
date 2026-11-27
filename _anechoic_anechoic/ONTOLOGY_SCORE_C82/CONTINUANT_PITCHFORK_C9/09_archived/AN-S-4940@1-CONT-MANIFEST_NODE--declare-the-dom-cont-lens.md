---
atom_family: SPEC
atom_id: AN-S-4940
concern:
  subject: Continuant Lens
  path: Model/Graph/Lens/Domain Lens
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T18:00:26.182530+00:00"
---
## Summary

Declare the DOM/CONT Lens

## Semantics

Continuant Declarations define the Domain Model.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class ContinuantLens(Lens):
    node.lens_path = value(fixed='DOM/CONT')
    node.control_flow = value(fixed='Declarative')
```
