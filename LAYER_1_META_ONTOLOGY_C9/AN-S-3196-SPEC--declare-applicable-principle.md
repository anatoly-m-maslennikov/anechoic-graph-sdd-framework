---
atom_family: SPEC
atom_id: AN-S-3196
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-21T18:17:21+00:00'
---

## Summary

Declare Applicable Principle

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Applicable Principle

## Claim

### Prose Claim

The Applicable Principle Template guides Project decisions when its
applicability conditions hold.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class ApplicablePrinciple(SpecAtom):
    pass

declare_entity(
    entity_name='Applicable Principle',
    entity_class=ApplicablePrinciple,
    entity_kind='Primary',
)
```
