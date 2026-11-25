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
  version: 5
  updated_at: '2026-11-12T02:59:39.478133+00:00'
---
## Summary

Declare Atom.Content.Claim.Formal Claim

## Claim

### Prose Claim

Formal Claim is a child Property of Claim. Its value contains one fenced formal expression. A Python fence is admitted when the affected consumers support the Python representation for that Claim. CFEL remains admitted during migration.
### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in RMED).Content.Claim.Formal Claim:: {::0..1};

Atom/(.Header.Context.Role in RMED).Content.Claim.Formal Claim.*[]{::0};

IF (Atom/(.Header.Context.Role in RMED).Content.Claim.Formal Claim {=1}) THEN (
FENCED_LABELS(Atom/(.Header.Context.Role in RMED).Content.Claim.Formal Claim):: [in (CFEL, python)]{::1}
)
```
