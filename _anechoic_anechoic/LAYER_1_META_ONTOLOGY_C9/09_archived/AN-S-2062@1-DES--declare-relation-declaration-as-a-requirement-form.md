---
atom_family: SPEC
atom_id: AN-S-2062
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 22:47:24 +0400
---

## Summary

Declare Relation Declaration as a Requirement Form

## Claim

### Prose Claim

This Form uses the Declaration contract.

### Formal Claim

```CFEL
# model
Atom//(.Header.Role := Requirement).Header.Form := Relation Declaration;
Atom//(.Header.Role := Requirement)//(.Header.Form := Relation Declaration)
```

## Semantics

A Relation Declaration defines a canonical binary Relation, its endpoint domains and applicable inverse aliases.
