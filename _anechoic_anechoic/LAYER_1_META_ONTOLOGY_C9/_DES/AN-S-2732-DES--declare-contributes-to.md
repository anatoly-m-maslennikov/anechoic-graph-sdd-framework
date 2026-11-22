---
atom_family: SPEC
atom_id: AN-S-2732
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare CONTRIBUTES_TO

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='CONTRIBUTES_TO',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```

## Semantics

The Host contributes toward the Target. Contribution is distinct from verified satisfaction of a Requirement.
