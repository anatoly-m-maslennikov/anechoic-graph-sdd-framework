---
atom_family: SPEC
atom_id: AN-S-2203
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-05 22:47:24 +0400
---
## Summary

Declare Atom/(.Header.Role := Plan).Header.Work Sequence Number

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Role: Plan).Header.Work Sequence Number:: [int]{::0..1};

Atom/(.Header.Role: Plan).Header.Work Sequence Number.*[]{::0};

# instances
Atom/(.Header.Role: Plan)//$atom;

IF ($atom.Header.Work Sequence Number{=1})
THEN ($atom.Header.Work Sequence Number > 0);

UNIQUE(
  Atom/(.Header.Role: Plan)//$atom_2,
  (.Header.Container.atom, .Header.Work Sequence Number),
  (.Header.Status = Active) AND (.Header.Work Sequence Number{=1}) AND (.Header.Container.atom{=1})
);

UNIQUE(
  Atom/(.Header.Role: Plan)//$atom_3,
  (.Header.Container.scope_unit, .Header.Work Sequence Number),
  (.Header.Status = Active) AND (.Header.Work Sequence Number{=1}) AND (.Header.Container.scope_unit{=1})
)
```
