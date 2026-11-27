---
atom_family: SPEC
atom_id: AN-S-3312
container:
  component: C9
tier: 2
context:
  lens: SPEC
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3313
  - AN-S-3314
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T11:27:38+00:00'
---

## Summary

Declare Project Contract Spec Template

## Semantics

A Project Contract describes the Project’s externally observable behavior.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import declare_template
from anechoic.model import Contract, Project

@declare_template(container=Project)
class ProjectContract(Contract):
    pass
```
