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
  version: 2
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Declare Atom.Header.Label

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Label: [string]{:0..1};

Atom.Header.Label.*[]{:0};

Atom.Header.Label ?= Atom.Header.Form
```
