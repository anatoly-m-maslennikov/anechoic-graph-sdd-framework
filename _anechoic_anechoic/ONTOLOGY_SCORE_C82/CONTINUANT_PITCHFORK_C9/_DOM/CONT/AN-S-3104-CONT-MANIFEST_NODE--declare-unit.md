---
atom_family: SPEC
atom_id: AN-S-3104
concern:
  subject: Unit
  path: Model/Graph/Node//Artifact//SSOT//Realization/Content/Module
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T14:46:18.792900+00:00"
---

## Summary

Declare Unit

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import ExecutableFile, Realization

class Unit(Realization):
    node.ssot_carrier = value(fixed=ExecutableFile)
```

## Semantics

The authoritative source is the Code Unit’s span within its Module file.
