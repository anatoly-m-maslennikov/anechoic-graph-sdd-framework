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
  version: 30
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Register rationale_for relation

## Claim scope

Rationale For Relation.

## Claim

`rationale_for` **means** the direct relation from a Rationale Analysis Atom
to the Atom that it explains.

```CFEL
((rationale_for)) >| Derivation == Direct;

Atom/(.Role: Analysis)/(.Form: Rationale)// ((rationale_for)) Atom//
```

## Semantics


Forward `Host ((rationale_for)) Target` and reverse `Target <((rationale_for)) Host` are views of the same Relation fact.
rationale_for relates Rationale Analysis Atom to explained Atom.

