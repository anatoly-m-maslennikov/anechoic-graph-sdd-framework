---
atom_family: SPEC
atom_id: AN-S-5007
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: archived
  version: 3
  updated_at: "2026-11-27T18:17:41.214410+00:00"
concern:
  subject: IO
  path: Model/Graph/Lens//SPEC//DES
  relation: is_narrower_than
---

## Summary

Declare the IO Lens

## Semantics

Groups the interfaces through which a system exchanges inputs and outputs.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import APILens, DesignLens

class IOLens(DesignLens):
    node.lens_path = value(fixed='IO')
    node.parts = {'API': APILens}
```

## Sources

- [ISO/IEC/IEEE 29148:2018 — Requirements engineering](https://www.iso.org/standard/72089.html) covers the specification of interface requirements.
