---
atom_family: SPEC
atom_id: AN-S-2631
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 30
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Register delivery_for relation

## Claim

### Prose Claim

#### Applicability
`delivery_for` relations.

`delivery_for` **means** the direct relation from a Delivery Atom to the Atom
that the Delivery realizes.

Forward `Host ((delivery_for)) Target` and reverse `Target <((delivery_for)) Host` are views of the same Relation fact.
delivery_for relates Delivery Atom to realized Atom.
### Formal Claim

```CFEL
# model
Relation//delivery_for ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom/(.Header.Context.Role: Delivery)//$atom ((delivery_for)) Atom//$atom_2
```

