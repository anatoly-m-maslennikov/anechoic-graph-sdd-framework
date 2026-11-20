---
identity:
  atom_id: AN-S-2203
context:
  container:
    component: C00
  tier: 3
  lens: DES
state:
  status: draft
  version: 2
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Declare Atom/(.Header.Role := Plan).Header.Work Sequence Number

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Role:=Plan).Header.Work Sequence Number :: [int]{::0..1};

Atom/(.Header.Role:=Plan).Header.Work Sequence Number.*[]{::0};

# instances
Atom/(.Header.Role:=Plan)//$atom;

IF ($atom.Header.Work Sequence Number{=1})
THEN ($atom.Header.Work Sequence Number > 0);

UNIQUE(
  Atom/(.Header.Role:=Plan)//$atom_2,
  (.Header.Container, .Header.Work Sequence Number),
  (.Header.Status = Active) AND (.Header.Work Sequence Number{=1}) AND (.Header.Container{=1})
)
```
