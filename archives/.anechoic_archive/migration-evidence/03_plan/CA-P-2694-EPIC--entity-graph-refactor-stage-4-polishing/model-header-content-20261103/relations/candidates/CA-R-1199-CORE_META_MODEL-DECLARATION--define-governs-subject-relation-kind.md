---
subjects:
  active: ANECHOIC_MODEL <+ CFEL <+ Relation//GOVERNS
  passive:
  - ANECHOIC_MODEL <+ CFEL > Relation
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Entity
  - ANECHOIC_MODEL <+ Atom.Content
version: 36
updated_at: 2026-11-02 08:06:47 +0400
atom_id: CA-R-1199
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Active
tier: 2
role: Requirement
form: Declaration
---
## Summary

Define GOVERNS Subject Relation Kind

## Claim

### Formal Claim

```CFEL
Relation//GOVERNS ((HAS_CLASSIFICATION)) Derivation == Direct;

Atom// ((GOVERNS)) $governed_subject
```

### Prose Claim

#### Applicability
the GOVERNS Subject Relation Kind.

GOVERNS **means** the direct Subject Relation Kind from an Atom **to** the canonical Subject graph node about which the Atom governs through its applicable role-specific content.

The Target is the canonical Subject about which the Atom governs through its applicable content.
Forward `Host ((GOVERNS)) Target` and reverse `Target <((GOVERNS)) Host` are views of the same Relation fact.
GOVERNS relates Atom to canonical Subject graph node.
