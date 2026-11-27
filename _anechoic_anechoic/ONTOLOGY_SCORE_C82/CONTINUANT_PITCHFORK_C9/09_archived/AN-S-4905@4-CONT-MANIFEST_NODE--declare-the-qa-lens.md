---
atom_family: SPEC
atom_id: AN-S-4905
concern:
  subject: QA
  path: Model/Graph/Lens//SPEC//SWE
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
  updated_at: "2026-11-26T18:18:20.893704+00:00"
---

## Summary

Declare the QA Lens

## Semantics

Groups quality criteria, verification methods, tests, and the evidence used to assess results.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SoftwareEngineeringLens

class QualityAssuranceLens(SoftwareEngineeringLens):
    node.lens_path = value(fixed='QA')
```
