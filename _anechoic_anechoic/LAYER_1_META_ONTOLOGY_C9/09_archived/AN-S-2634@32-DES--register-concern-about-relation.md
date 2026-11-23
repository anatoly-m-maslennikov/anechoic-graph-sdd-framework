---
atom_family: SPEC
atom_id: AN-S-2634
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

Register concern_about relation

## Claim

### Prose Claim

#### Applicability
`concern_about` relations.

`concern_about` **means** the direct relation from a Concern Atom to the
governed entity that it concerns.

The Host is a Concern Atom; the governed target is the Entity concerned.
Forward `Host ((concern_about)) Target` and reverse `Target <((concern_about)) Host` are views of the same Relation fact.
concern_about relates Concern Atom to governed entity concerned.

#### Details
Endpoint admission is an Atom Entity Definition concern, not Relation Definition
metadata.
### Formal Claim

```CFEL
# model
Relation//concern_about ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom/(.Header.Context.Role: Concern)//$atom ((concern_about)) $governed
```

