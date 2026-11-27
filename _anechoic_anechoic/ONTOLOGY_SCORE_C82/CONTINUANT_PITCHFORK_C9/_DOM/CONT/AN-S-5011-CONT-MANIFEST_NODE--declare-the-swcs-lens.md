---
atom_family: SPEC
atom_id: AN-S-5011
concern:
  subject: SWCS
  path: Model/Graph/Lens//SPEC//SWE//SWD
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 1
  updated_at: '2026-11-26T18:18:17.079954+00:00'
---

## Summary

Declare the SWCS Lens

## Semantics

Defines rules for organizing and writing executable code.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SoftwareDevelopmentLens

class SoftwareCodeStandardsLens(SoftwareDevelopmentLens):
    node.lens_path = value(fixed='SWD/SWCS')
```

## Sources

- [ISO/IEC 5055:2021 — Automated source code quality measures](https://www.iso.org/standard/80623.html) provides source code quality measures.
