---
atom_family: SPEC
atom_id: AN-S-5008
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 2
  updated_at: '2026-11-26T18:18:17.071599+00:00'
concern:
  subject: SWE
  path: Model/Graph/Lens//SPEC
  relation: is_narrower_than
---

## Summary

Declare the SWE Lens

## Semantics

Groups software development, quality assurance, and operations.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SpecificationLens, SoftwareDevelopmentLens, QualityAssuranceLens, DevOpsLens

class SoftwareEngineeringLens(SpecificationLens):
    node.lens_path = value(fixed='SWE')
    node.parts = {
        'SWD': SoftwareDevelopmentLens,
        'QA': QualityAssuranceLens,
        'DevOps': DevOpsLens,
    }
```

## Sources

- [ISO/IEC/IEEE 12207:2026 — Software life cycle processes](https://www.iso.org/standard/90219.html)
