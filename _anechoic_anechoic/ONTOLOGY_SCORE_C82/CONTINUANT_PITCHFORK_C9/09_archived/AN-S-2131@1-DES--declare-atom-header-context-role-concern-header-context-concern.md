---
atom_family: SPEC
atom_id: AN-S-2131
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

Declare Atom/(.Header.Context.Role := Concern).Header.Context.Concern

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Concern)).Header.Context.Concern{::1} :: []{::0};

Atom/(.Header.Context.Role in (Concern)).Header.Context.Concern.*[in (Priority)]{::1}
```
