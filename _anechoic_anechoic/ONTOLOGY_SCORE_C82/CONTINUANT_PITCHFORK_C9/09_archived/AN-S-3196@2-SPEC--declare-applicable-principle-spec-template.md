---
atom_family: SPEC
atom_id: AN-S-3196
container:
  component: C9
tier: 2
context:
  lens: SPEC
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3197
  - AN-S-3198
  - AN-S-3302
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T11:27:38+00:00'
---

## Summary

Declare Applicable Principle Spec Template

## Semantics

An Applicable Principle guides Project decisions when its applicability conditions hold.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import declare_template
from anechoic.model import Project, SpecAtom

@declare_template(tier=(1, 2), container=Project)
class ApplicablePrinciple(SpecAtom):
    pass
```
