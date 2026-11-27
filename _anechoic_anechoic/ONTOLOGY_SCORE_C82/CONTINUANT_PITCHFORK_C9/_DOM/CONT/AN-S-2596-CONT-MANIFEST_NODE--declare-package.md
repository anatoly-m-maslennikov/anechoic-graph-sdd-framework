---
atom_family: SPEC
atom_id: AN-S-2596
concern:
  subject: Package
  path: Model/Graph/Node//Artifact//SSOT//Realization/Structure
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 10
  updated_at: "2026-11-26T14:46:18.716125+00:00"
---

## Summary

Declare Package

## Semantics

A local Package kind follows the postfix of its folder name. The reserved postfixes are `__tests`, `__agentic`, and `__assets`.

The actual Package folder establishes the Package’s identity and membership.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Folder, Realization

class Package(Realization):
    node.ssot_carrier = value(fixed=Folder)
```
