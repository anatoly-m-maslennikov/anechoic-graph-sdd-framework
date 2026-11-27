---
atom_family: SPEC
atom_id: AN-S-4840
concern:
  subject: Asset
  path: Model/Graph/Node//Artifact//SSOT//Realization/Content
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 2
  updated_at: "2026-11-26T14:46:18.824761+00:00"
---

## Summary

Declare Asset

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import NonExecutableFile, Realization

class Asset(Realization):
    node.ssot_carrier = value(fixed=NonExecutableFile)
```

## Semantics

The source file stores the Asset.
