---
atom_family: PROJECT_CONFIG
atom_id: AN-C-3194
structure:
  container:
    component: C00
context:
  template: manifest_node
relations:
  IS_REPLACEMENT_FOR:
  - AN-C-3193
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T17:13:49.319594+00:00"
concern:
  subject: Axiom
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification
  relation: is_narrower_than
---

## Summary

Declare Axiom Spec Template

## Semantics

An Axiom states an accepted premise for the Project within the context of the Project Goal.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens, Project, SpecAtom

class Axiom(SpecAtom):
    node.tier = value(fixed=0)
    node.lens = value(fixed=Lens.SPEC)
    node.container_type = value(fixed=Project)
```
