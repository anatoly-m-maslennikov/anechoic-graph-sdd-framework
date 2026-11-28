---
atom_family: SPEC
atom_id: AN-S-4907
concern:
  subject: SWD
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
  version: 6
  updated_at: "2026-11-28T15:16:37.698017+00:00"
---

## Summary

Declare the SWD Lens

## Semantics

Groups engineering rules for implementing and maintaining software.

`SWD = DBT + SWA + SWCS + Internal API`.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import (
    SoftwareEngineeringLens, DataBuildToolLens, SoftwareArchitectureLens,
    InternalAPILens, SoftwareCodeStandardsLens,
)

class SoftwareDevelopmentLens(SoftwareEngineeringLens):
    node.lens_path = value(fixed='SWD')
    node.parts = {
        'DBT': DataBuildToolLens,
        'SWA': SoftwareArchitectureLens,
        'SWCS': SoftwareCodeStandardsLens,
        'INTERNAL_API': InternalAPILens,
    }
```

## Sources

- [ISO/IEC/IEEE 12207:2026 — Software life cycle processes](https://www.iso.org/standard/90219.html)
