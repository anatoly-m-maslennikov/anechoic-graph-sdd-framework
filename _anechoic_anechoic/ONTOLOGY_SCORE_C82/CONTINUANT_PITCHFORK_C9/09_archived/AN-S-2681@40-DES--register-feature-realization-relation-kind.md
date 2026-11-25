---
atom_family: SPEC
atom_id: AN-S-2681
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 40
  updated_at: "2026-11-25T22:50:36.514661+00:00"
---
## Summary

Register feature realization relation kind

## Claim

### Prose Claim

#### Applicability
a declared SPEC Feature Scope Unit and its applicable native Realization targets.

`HAS_FEATURE_REALIZATION` **must** be registered as a typed relation that maps a declared SPEC Feature Scope Unit **to** its applicable native Realization targets **without** making those targets Scope Units.

The Host is a SPEC Feature Scope Unit and the Target is its applicable native Realization.
Forward `Host ((HAS_FEATURE_REALIZATION)) Target` and reverse `Target <((HAS_FEATURE_REALIZATION)) Host` are views of the same Relation fact.
HAS_FEATURE_REALIZATION relates SPEC Feature Scope Unit to applicable native Realization target.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='HAS_FEATURE_REALIZATION',
    source_endpoint={'level': 'instances', 'entity_paths': ('Scope Unit',)},
    target_endpoint={'level': 'instances'},
)
```
