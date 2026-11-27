---
atom_family: SPEC
atom_id: AN-S-5009
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 3
  updated_at: '2026-11-26T18:18:17.075719+00:00'
concern:
  subject: SYS
  path: Model/Graph/Lens//SPEC
  relation: is_narrower_than
---

## Summary

Declare the SYS Lens

## Semantics

Groups the Domain and engineering concerns of a system.

`SYS = DOM + SWE`.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SpecificationLens, SoftwareEngineeringLens, DomainLens

class SystemLens(SpecificationLens):
    node.lens_path = value(fixed='SYS')
    node.parts = {
        '=>DOM': DomainLens,
        '=>SWE': SoftwareEngineeringLens,
    }
```

## Sources

- [ISO/IEC/IEEE 15288:2023 — System life cycle processes](https://www.iso.org/standard/81702.html)
