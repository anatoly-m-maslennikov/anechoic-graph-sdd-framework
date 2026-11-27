---
atom_family: SPEC
atom_id: AN-S-5010
concern:
  subject: SWA
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
  updated_at: '2026-11-26T18:18:17.077298+00:00'
---

## Summary

Declare the SWA Lens

## Semantics

Describes the structure, interfaces, and rationale of software architecture.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SoftwareDevelopmentLens

class SoftwareArchitectureLens(SoftwareDevelopmentLens):
    node.lens_path = value(fixed='SWD/SWA')
```

## Sources

- [ISO/IEC/IEEE 42010:2022 — Architecture description](https://www.iso.org/standard/74393.html)
- [The Open Group — TOGAF Standard, 10th Edition](https://help.opengroup.org/hc/en-us/articles/32726995273362-Understanding-the-TOGAF-Standard)
