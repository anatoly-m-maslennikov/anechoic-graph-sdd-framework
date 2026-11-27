---
atom_family: SPEC
atom_id: AN-S-4906
concern:
  subject: SPEC
  path: Model/Graph/Lens
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
  updated_at: '2026-11-26T18:18:17.053743+00:00'
---

## Summary

Declare the SPEC Lens

## Semantics

Groups definitions and constraints that specify the Model and its instances.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens, DesignLens, SoftwareEngineeringLens, SystemLens, IOLens

class SpecificationLens(Lens):
    node.lens_path = value(fixed='SPEC')
    node.parts = {
        'DES': DesignLens,
        'SWE': SoftwareEngineeringLens,
        'SYS': SystemLens,
        '=>IO': IOLens,
    }
    node.alternatives = (('DES', 'SWE'), ('SYS', '=>IO'))
```

## Sources

- [ISO/IEC/IEEE 29148:2018 — Requirements engineering](https://www.iso.org/standard/72089.html)
