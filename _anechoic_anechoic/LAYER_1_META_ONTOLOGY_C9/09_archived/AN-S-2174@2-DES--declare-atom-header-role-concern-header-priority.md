---
atom_family: SPEC
atom_id: AN-S-2174
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-11 16:04:42 +0400
---
## Summary

Declare Atom/(.Header.Role := Concern).Header.Priority

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Concern)).Header.Context.Concern.Priority{::1}:: [string]{::1};

Atom/(.Header.Context.Role in (Concern)).Header.Context.Concern.Priority.*[]{::0};

Atom/(.Header.Context.Role in (Concern)).Header.Context.Concern.Priority :: High;

Atom/(.Header.Context.Role in (Concern)).Header.Context.Concern.Priority :: Medium;

Atom/(.Header.Context.Role in (Concern)).Header.Context.Concern.Priority :: Low
```
