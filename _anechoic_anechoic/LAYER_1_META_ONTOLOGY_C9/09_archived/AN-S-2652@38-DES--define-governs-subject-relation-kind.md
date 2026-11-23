---
atom_family: SPEC
atom_id: AN-S-2652
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 38
  updated_at: 2026-11-04 03:22:03 +0400
---
## Summary

Define GOVERNS Subject Relation Kind

## Claim

### Prose Claim

#### Applicability
the GOVERNS Subject Relation Kind.

GOVERNS **means** the direct Subject Relation Kind from an Atom **to** the canonical Subject entity or instance about which the Atom governs through its applicable role-specific content.

The Target is the canonical Subject about which the Atom governs through its applicable content.
Forward `Host ((GOVERNS)) Target` and reverse `Target <((GOVERNS)) Host` are views of the same Relation fact.
GOVERNS relates Atom to canonical Subject entity or instance.
### Formal Claim

```CFEL
# model
Relation//GOVERNS ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom//$atom ((GOVERNS)) $governed_subject
```

