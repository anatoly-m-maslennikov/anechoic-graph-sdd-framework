---
atom_family: SPEC
atom_id: AN-S-2680
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 38
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Register derived_from relation

## Claim

### Prose Claim

#### Applicability
direct derivation relations between exact represented content versions.

DERIVED_FROM means the directed Relation from a derived represented content version to an exact source content version used to derive it. Version references identify the relevant states; this does not introduce a Revision entity.

The Host is a derived represented-content version and the Target is the exact source content version used to derive it.
Forward `Host ((DERIVED_FROM)) Target` and reverse `Target <((DERIVED_FROM)) Host` are views of the same Relation fact.
DERIVED_FROM relates derived represented content version to exact source content version.
### Formal Claim

```CFEL
# model
Relation//DERIVED_FROM ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
$derived_content_version ((DERIVED_FROM)) $source_content_version
```

