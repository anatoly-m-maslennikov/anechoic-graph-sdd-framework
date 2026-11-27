---
atom_family: SPEC
atom_id: AN-S-4905
concern:
  subject: Quality Assurance Lens
  path: Model/Graph/Lens
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
  updated_at: "2026-11-26T18:00:26.207117+00:00"
---

## Summary

Declare the QA Lens

## Semantics

Groups quality criteria, verification methods, tests, and the evidence used to assess results.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class QualityAssuranceLens(Lens):
    node.lens_path = value(fixed='QA')
```
