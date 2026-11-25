---
atom_family: SPEC
atom_id: AN-S-2234
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-02 08:06:47 +0400
---

## Summary

Require one Declaration for each Node

## Claim

### Prose Claim


Evaluate ownership within the selected effective MODEL. Each member selected by (Node, Node.**), including the root and each Property, has exactly one effective Current authoritative Requirement/Form: Declaration addressing that Node.

Count inherited Current Declarations and explicit local replacements after MODEL override resolution. A replaced base Declaration remains available in its base MODEL and is not a second effective owner in the local MODEL. Drafts and archives are not Current owners. Other Atoms may address the same Node.


The count uses only the effective Current Declaration-to-Node links in that MODEL. HAS_ACTIVE_SUBJECT is the canonical Relation obtained from the dedicated active Subject field; obtaining its value from that field does not make it a derived view of another Relation.
### Formal Claim

```CFEL
# instances
Atom/(.Header.Context.Role: Requirement)/(.Header.Context.Form: Declaration)//$atom ((HAS_ACTIVE_SUBJECT)){::1} (Node, Node.**)
```

