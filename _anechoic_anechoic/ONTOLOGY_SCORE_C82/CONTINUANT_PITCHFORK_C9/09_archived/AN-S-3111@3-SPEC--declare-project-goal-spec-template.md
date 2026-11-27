---
atom_family: SPEC
atom_id: AN-S-3111
container:
  component: C9
tier: 2
context:
  lens: SPEC
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3127
  - AN-S-3152
  - AN-S-3301
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T11:27:38+00:00'
---

## Summary

Declare Project Goal Spec Template

## Semantics

A Project Goal states the intended outcome of the Project.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import declare_template
from anechoic.model import Lens, Project, Purpose

@declare_template(tier=-1, container=Project, encapsulation="black_box", lens=Lens.SPEC)
class ProjectGoal(Purpose):
    pass
```
