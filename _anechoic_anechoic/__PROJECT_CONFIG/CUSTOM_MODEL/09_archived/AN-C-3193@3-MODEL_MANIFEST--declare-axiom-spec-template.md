---
atom_family: PROJECT_CONFIG
atom_id: AN-C-3193
structure:
  container:
    component: C00
context:
  template: model_manifest
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3193
  - AN-S-3194
  - AN-S-3195
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T11:20:07+00:00'
---

## Summary

Declare Axiom Spec Template

## Semantics

An Axiom states an accepted premise for the Project within the context of the Project Goal.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import declare_template
from anechoic.model import Lens, Project, SpecAtom

@declare_template(tier=0, container=Project, lens=Lens.SPEC)
class Axiom(SpecAtom):
    pass
```

