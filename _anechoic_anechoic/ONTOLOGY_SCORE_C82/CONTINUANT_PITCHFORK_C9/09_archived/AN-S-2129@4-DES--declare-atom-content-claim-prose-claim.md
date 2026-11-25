---
atom_family: SPEC
atom_id: AN-S-2129
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-07 17:10:31 +0400
---

## Summary

Declare Atom.Content.Claim.Prose Claim

## Claim

### Prose Claim

Prose Claim is a child Property of Claim. Its value is ordinary Markdown; headings within that value are not Properties unless an applicable declaration admits them.
### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in RMED).Content.Claim.Prose Claim:: {::0..1};

Atom/(.Header.Context.Role in RMED).Content.Claim.Prose Claim.*[]{::0}
```
