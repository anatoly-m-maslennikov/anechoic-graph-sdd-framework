---
atom_family: SPEC
atom_id: AN-S-2164
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Declare Scope Unit ID

## Claim

### Formal Claim

```CFEL
# model
Scope Unit.ID:: [string]{::1};

Scope Unit.ID.*[]{::0};

# instances
Scope Unit//$unit;

$unit.ID{::1}
```

## Semantics

Every Scope Unit has a stable ID. A non-root Scope Unit keeps its ID through moves and renames; the ID distinguishes those operations from removal. `CA-SU--1` identifies the predefined Scope Unit named `world`.
