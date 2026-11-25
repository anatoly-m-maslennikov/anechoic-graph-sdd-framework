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
  version: 1
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Declare Atom/(.Header.Role := Concern).Header.Priority

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Role: Concern).Header.Priority{::1}:: [string]{::1};

Atom/(.Header.Role: Concern).Header.Priority.*[]{::0};

Atom/(.Header.Role: Concern).Header.Priority: High;

Atom/(.Header.Role: Concern).Header.Priority: Medium;

Atom/(.Header.Role: Concern).Header.Priority: Low
```
