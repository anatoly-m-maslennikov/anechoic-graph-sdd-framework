---
atom_family: SPEC
atom_id: AN-S-2628
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 32
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Register rationale_for relation

## Claim

### Prose Claim

#### Applicability
Rationale For Relation.

`rationale_for` **means** the direct relation from a Rationale Analysis & Advisory Atom
to the Atom that it explains.

Forward `Host ((rationale_for)) Target` and reverse `Target <((rationale_for)) Host` are views of the same Relation fact.
rationale_for relates Rationale Analysis & Advisory Atom to explained Atom.
### Formal Claim

```CFEL
# model
Relation//rationale_for ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom/(.Header.Role: "Analysis & Advisory")/(.Header.Form: Rationale)//$atom ((rationale_for)) Atom//$atom_2
```

