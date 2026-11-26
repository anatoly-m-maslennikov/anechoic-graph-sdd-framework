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
  version: 1
  updated_at: "2026-11-25T12:40:53.388819+00:00"
relations:
  IS_REFERENCE:
  - AN-T-3922@1
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
    lens_path = value(fixed='QA')
```
