---
atom_family: SPEC
atom_id: AN-S-2011
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: '2026-11-11T18:56:17+04:00'
---

## Summary

Declare Atom/(.Role := Requirement)

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Role :: Requirement;

Atom/(.Header.Context.Role := Requirement) >| (Role Order Number == 4);
```

## Semantics

A Requirement states a required outcome, behavior, property or constraint, or defines a governed model and its constraints. It applies across Aspects, including domain behavior, engineering performance, evaluation effectiveness and delivery reliability.
