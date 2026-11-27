---
atom_family: SPEC
atom_id: AN-S-4824
concern:
  subject: Prescribed
  path: Model/Graph/Node//Artifact//SSOT
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T17:13:49.187137+00:00"
---

## Summary

Declare Prescribed

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import SSOT

class Prescribed(SSOT):
    pass
```
