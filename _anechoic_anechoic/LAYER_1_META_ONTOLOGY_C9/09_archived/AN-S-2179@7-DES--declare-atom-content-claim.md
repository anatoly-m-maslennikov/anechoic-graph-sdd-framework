---
atom_family: SPEC
atom_id: AN-S-2179
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: '2026-11-12T02:59:39.799698+00:00'
---
## Summary

Declare Atom.Content.Claim

## Claim

### Prose Claim

A complete ordinary RMED Claim has at least one of Formal Claim and Prose Claim. Sibling names are unique. Formal Claim uses the fenced language admitted by its declaration. Prose Claim contains ordinary Markdown. A Markdown heading inside Prose Claim is part of its value, unless an applicable declaration expressly declares it as a child Property.

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in RMED).Content.Claim{::1}:: []{::0};

Atom/(.Header.Context.Role in RMED).Content.Claim.*[string, in (Formal Claim, Prose Claim)]{::1..2};

Atom/(.Header.Context.Role in RMED).Content.Claim.Prose Claim ;> Atom/(.Header.Context.Role in RMED).Content.Claim.Formal Claim
```
