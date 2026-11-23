---
atom_family: SPEC
atom_id: AN-S-2594
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 11
  updated_at: 2026-11-11 15:37:01 +0400
---

## Summary

Declare Atom/(.Role := Plan)

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Role :: Plan;

Atom/(.Header.Context.Role in (Plan)) >| (Container == yes);

Atom/(.Header.Context.Role in (Plan));

# instances
Atom/(.Header.Context.Role in (Plan))//$plan {::0+}((CONTAINS)) Atom/(.Header.Context.Role in (Plan))//$contained_plan;

Atom/(.Header.Context.Role in (Plan))//$dependent {::0+}((IS_BLOCKED_BY)) Atom/(.Header.Context.Role in (Plan))//$prerequisite;

Atom/(.Header.Context.Role in (Plan))//$prerequisite_2 {::0+}((BLOCKS)) Atom/(.Header.Context.Role in (Plan))//$dependent_2;

FOR EACH $atom[<Atom>, (.Header.Context.Role = Plan)]:
(
    IF (($atom.Header.State.Status = Active) AND ($atom.Header.Context.Plan.Work Sequence Number{=1}))
    THEN ($atom.Header.Context.Container{==1})
);

FOR EACH $parent[<Atom>, ((.Header.Context.Role = Plan) AND (.Header.State.Status in (Done, Canceled)))]:
(
    FOR EACH $descendant[<Atom>, ((.Header.Context.Role = Plan) AND (.Header.State.Status >| Status Group = Current))]:
    (
        IF ($parent ((RECURSIVELY_CONTAINS)) $descendant)
        THEN ($descendant.Header.State.Status :: [in (Done, Canceled)]{::1})
    )
)
```

## Semantics

A Plan describes intended work, an intended outcome or its execution record. Work Report is the Form for that execution record.
