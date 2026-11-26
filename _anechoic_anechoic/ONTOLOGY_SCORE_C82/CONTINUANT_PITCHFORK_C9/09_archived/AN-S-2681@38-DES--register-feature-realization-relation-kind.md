---
atom_family: SPEC
atom_id: AN-S-2681
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 38
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Register feature realization relation kind

## Claim

### Prose Claim

#### Applicability
a declared SPEC Feature Scope Unit and its applicable native Realization targets.

`feature_realization` **must** be registered as a typed relation that maps a declared SPEC Feature Scope Unit **to** its applicable native Realization targets **without** making those targets Scope Units.

The Host is a SPEC Feature Scope Unit and the Target is its applicable native Realization.
Forward `Host ((feature_realization)) Target` and reverse `Target <((feature_realization)) Host` are views of the same Relation fact.
feature_realization relates SPEC Feature Scope Unit to applicable native Realization target.
### Formal Claim

```CFEL
# model
Relation//feature_realization ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Scope Unit//$scope_unit ((feature_realization)) $realization_target
```

