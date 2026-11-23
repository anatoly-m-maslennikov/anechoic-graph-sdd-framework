---
atom_family: SPEC
atom_id: AN-S-2630
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

Register Evaluation targets

## Claim

### Prose Claim

#### Applicability
direct `evaluation_for` relations.

`evaluation_for` **means** the direct relation from an Evaluation Atom to an
Atom whose authority the Evaluation checks.

Forward `Host ((evaluation_for)) Target` and reverse `Target <((evaluation_for)) Host` are views of the same Relation fact.
evaluation_for relates Evaluation Atom to Atom whose authority is evaluated.
### Formal Claim

```CFEL
# model
Relation//evaluation_for ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom/(.Header.Context.Role: Evaluation)//$atom ((evaluation_for)) Atom//$atom_2
```

