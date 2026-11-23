---
atom_family: SPEC
atom_id: AN-S-2196
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Declare Atom.Content.Summary

## Claim

### Formal Claim

```CFEL
# model
Atom.Content.Summary{::1}:: {::1};

Atom.Content.Summary.*[]{::0};

# instances
DETERMINES(
  Atom//$atom,
  (.Header.Identity.ID),
  (.Content.Summary),
  (Atom.Header.State.Status >| Status Group = Current) OR (Atom.Header.State.Status >| Status Group = Archived)
)
```

