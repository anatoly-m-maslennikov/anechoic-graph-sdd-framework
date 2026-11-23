---
atom_family: SPEC
atom_id: AN-S-2127
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 09:19:08 +0400
---
## Summary

Declare Atom.Header.Tier

## Claim

### Prose Claim

Atom.Header.Tier stores one integer value and an optional Tier Label; the Formal Claim defines their representation.

### Formal Claim

```CFEL
# model
Atom.Header.Context.Tier{::1}:: [int]{::1};

Atom.Header.Context.Tier.*[in(Label)]{::0..1};

Atom.Header.Context.Tier >= -1
```
