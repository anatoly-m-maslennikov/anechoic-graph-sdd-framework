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
  version: 5
  updated_at: 2026-11-11 16:04:42 +0400
---
## Summary

Declare Atom/(.Header.Role := Plan).Header.Work Sequence Number

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Plan)).Header.Context.Plan.Work Sequence Number:: [int]{::0..1};

Atom/(.Header.Context.Role in (Plan)).Header.Context.Plan.Work Sequence Number.*[]{::0};

# instances
Atom/(.Header.Context.Role in (Plan))//$atom;

IF ($atom.Header.Context.Plan.Work Sequence Number{=1})
THEN ($atom.Header.Context.Plan.Work Sequence Number > 0);

UNIQUE(
  Atom/(.Header.Context.Role in (Plan))//$atom_2,
  (.Header.Context.Container.atom, .Header.Context.Plan.Work Sequence Number),
  (.Header.State.Status = Active) AND (.Header.Context.Plan.Work Sequence Number{=1}) AND (.Header.Context.Container.atom{=1})
);

UNIQUE(
  Atom/(.Header.Context.Role in (Plan))//$atom_3,
  (.Header.Context.Container.scope_unit, .Header.Context.Plan.Work Sequence Number),
  (.Header.State.Status = Active) AND (.Header.Context.Plan.Work Sequence Number{=1}) AND (.Header.Context.Container.scope_unit{=1})
)
```
