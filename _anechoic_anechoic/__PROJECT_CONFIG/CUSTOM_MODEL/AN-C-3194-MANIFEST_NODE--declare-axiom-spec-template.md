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
  status: active
  version: 5
  updated_at: '2026-11-27T17:50:26.617704+00:00'
concern:
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//.Header.Context
  relation: .
  subject: Template := axiom
---

## Summary

Declare Axiom Spec Template

## Semantics

An Axiom states an accepted premise for the Project within the context of the Project purpose.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens, Project, SpecAtom

class Axiom(SpecAtom):
    node.template = value(fixed='axiom')
    node.tier = value(fixed=0)
    node.lens = value(fixed=Lens.SPEC)
    node.container_type = value(fixed=Project)
```
