---
atom_family: SPEC
atom_id: AN-S-2275
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T22:48:43.080209+00:00"
---

## Summary

Declare Requirement Solution Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement

class RequirementSolution(Requirement):
    pass

declare_entity(
    entity_class=RequirementSolution,
    entity_name='Solution',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Solution specifies the contribution that realizes a Scope Unit’s responsibility across the unit and its descendants. Its Role identifies the contribution.
