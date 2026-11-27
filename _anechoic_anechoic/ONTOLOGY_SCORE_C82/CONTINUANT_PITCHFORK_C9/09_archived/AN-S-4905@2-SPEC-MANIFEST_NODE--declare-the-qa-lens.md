---
atom_family: SPEC
atom_id: AN-S-4905
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.388634+00:00"

---

## Summary

Declare the QA Lens

## Semantics

Groups quality criteria, verification methods, tests, and the evidence used to assess results.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/Quality Assurance Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class QualityAssuranceLens(Lens):
    node.lens_path = value(fixed='QA')
```
