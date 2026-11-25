---
atom_family: PROJECT_CONFIG
atom_id: AN-C-3193
structure:
  container:
    component: C00
context:
  template: manifest_node
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3193
  - AN-S-3194
  - AN-S-3195
state:
  status: draft
  version: 4
  updated_at: '2026-11-24T15:59:19+00:00'
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
    tier = value(fixed=0)
    lens = value(fixed=Lens.SPEC)
    container_type = value(fixed=Project)
```
