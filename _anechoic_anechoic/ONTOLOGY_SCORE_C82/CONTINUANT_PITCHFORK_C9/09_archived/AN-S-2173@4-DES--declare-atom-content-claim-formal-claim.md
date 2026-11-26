---
atom_family: SPEC
atom_id: AN-S-2173
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

Declare Atom.Content.Claim.Formal Claim

## Claim

### Prose Claim

Formal Claim is a child Property of Claim. Its value is Markdown and contains a CFEL-labelled code fence.
### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in RMED).Content.Claim.Formal Claim:: {::0..1};

Atom/(.Header.Context.Role in RMED).Content.Claim.Formal Claim.*[]{::0};

IF (Atom/(.Header.Context.Role in RMED).Content.Claim.Formal Claim {=1}) THEN (
FENCED_LABELS(Atom/(.Header.Context.Role in RMED).Content.Claim.Formal Claim):: [in (CFEL)]{::1}
)
```
