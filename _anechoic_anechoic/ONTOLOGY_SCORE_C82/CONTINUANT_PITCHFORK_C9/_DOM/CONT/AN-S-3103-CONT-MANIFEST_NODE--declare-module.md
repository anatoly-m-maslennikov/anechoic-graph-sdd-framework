---
atom_family: SPEC
atom_id: AN-S-3103
concern:
  subject: Module
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
  version: 5
  updated_at: "2026-11-26T14:46:18.778141+00:00"
---

## Summary

Declare Module

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import ExecutableFile, Realization

class Module(Realization):
    node.ssot_carrier = value(fixed=ExecutableFile)
```

## Claim

Each Module belongs to one Package. A Module directly in the realization root belongs to the Project Realization.

## Semantics

Use the actual executable file and its Project-relative path to locate the Module.
