---
atom_family: SPEC
atom_id: AN-S-2052
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 07:31:50 +0400
---
## Summary

Declare Atom.Header.Subjects

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Topics{::1}:: []{::0};

Atom.Header.Context.Topics.*[in(Main Subject, Dependencies)]{::1..2}
```
