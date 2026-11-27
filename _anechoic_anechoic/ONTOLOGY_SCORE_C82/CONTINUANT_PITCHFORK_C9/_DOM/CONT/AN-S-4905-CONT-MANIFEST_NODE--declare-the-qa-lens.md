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
  status: active
  version: 5
  updated_at: '2026-11-26T18:18:17.051330+00:00'
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

## Sources

- [ISO/IEC 25010:2023 — Product quality model](https://www.iso.org/standard/78176.html)
- [ISO/IEC/IEEE 29119-2:2021 — Test processes](https://www.iso.org/standard/79428.html)
