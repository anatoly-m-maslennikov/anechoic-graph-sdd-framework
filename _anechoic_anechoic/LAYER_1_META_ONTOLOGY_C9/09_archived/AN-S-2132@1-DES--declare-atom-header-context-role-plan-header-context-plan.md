---
atom_family: SPEC
atom_id: AN-S-2132
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 16:27:40 +0400
---

## Summary

Declare Atom/(.Header.Context.Role := Plan).Header.Context.Plan

## Claim

### Prose Claim

The Plan group is present only for an Atom with Plan Role and is omitted when it would contain no declared Property.

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Plan)).Header.Context.Plan{::0..1} :: []{::0};

Atom/(.Header.Context.Role in (Plan)).Header.Context.Plan.*[in (Work Sequence Number, AI Agent Confidence Threshold)]{::1..2}
```
