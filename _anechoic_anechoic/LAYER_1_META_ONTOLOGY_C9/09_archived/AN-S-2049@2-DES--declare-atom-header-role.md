---
atom_family: SPEC
atom_id: AN-S-2049
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-11T18:56:17+04:00'
---
## Summary

Declare Atom.Header.Role

## Claim


### Prose Claim

Role Order Number classifies the Role-qualified Atom kind in the Model. Each Role Declaration assigns exactly one positive integer. Order numbers are distinct across Roles. Gaps are allowed.

### Formal Claim

```CFEL
# model
Atom.Header.Context.Role{::1}:: [string]{::1};

Atom.Header.Context.Role.*[]{::0}
```
