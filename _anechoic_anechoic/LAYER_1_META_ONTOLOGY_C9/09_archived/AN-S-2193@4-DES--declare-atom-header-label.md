---
atom_family: SPEC
atom_id: AN-S-2193
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-04 20:33:16 +0400
---
## Summary

Declare Atom.Header.Label

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Label:: [string]{::0..1};

Atom.Header.Context.Label.*[]{::0};

# instances
Atom//$atom;

$atom.Header.Context.Label ?== $atom.Header.Context.Form
```
