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
  version: 6
  updated_at: '2026-11-11T18:31:44+04:00'
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
  (Atom.Header.State.Status >| Status Group = Current) OR (Atom.Header.State.Status >| Status Group = Backlog) OR (Atom.Header.State.Status >| Status Group = Archived)
)
```

