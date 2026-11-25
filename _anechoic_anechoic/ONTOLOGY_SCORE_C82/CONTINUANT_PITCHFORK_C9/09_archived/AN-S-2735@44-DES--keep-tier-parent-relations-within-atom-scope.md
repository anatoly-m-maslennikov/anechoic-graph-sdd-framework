---
atom_family: SPEC
atom_id: AN-S-2735
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 44
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Keep tier-parent relations within Atom Scope

## Claim

### Prose Claim

#### Applicability
The existing governing child_of relation, pending its separately planned replacement.

child_of is the directed governing connection from a child Atom to the parent Atom whose Claim governs that child's contribution. It is distinct from containment, dependency, classification and source-layer membership. The Atom definition CA-R-2508 and ordering definition CA-R-2149 govern endpoint admission and ordering. This definition preserves the existing relation until its separate replacement Epic; it does not migrate its actual links.

Forward `Host ((child_of)) Target` and reverse `Target <((child_of)) Host` are views of the same Relation fact.
child_of relates child Atom to parent Atom.
### Formal Claim

```CFEL
# model
Relation//child_of ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom//$atom ((child_of)) Atom//$atom_2;
```

