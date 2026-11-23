---
atom_family: SPEC
atom_id: AN-S-4343
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T20:07:45.645838+00:00'
---

## Summary

Declare Requirement Direct Policy Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement

class DirectPolicy(Requirement):
    pass

declare_entity(
    entity_class=DirectPolicy,
    entity_name='Direct Policy',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Direct Policy applies to all descendants recursively without a local copy. A genuine SPECIALIZES Atom may add applicable detail while preserving parent constraints.
