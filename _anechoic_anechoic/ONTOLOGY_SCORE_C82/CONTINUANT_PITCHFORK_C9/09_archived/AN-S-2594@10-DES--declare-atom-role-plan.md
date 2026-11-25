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
  version: 10
  updated_at: 2026-11-11 14:06:22 +0400
---

## Summary

Declare Atom/(.Role := Plan)

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Role :: Plan;

Atom/(.Header.Role in (Plan)) >| (Container == yes);

Atom/(.Header.Role in (Plan));

# instances
Atom/(.Header.Role in (Plan))//$plan {::0+}((CONTAINS)) Atom/(.Header.Role in (Plan))//$contained_plan;

Atom/(.Header.Role in (Plan))//$dependent {::0+}((IS_BLOCKED_BY)) Atom/(.Header.Role in (Plan))//$prerequisite;

Atom/(.Header.Role in (Plan))//$prerequisite_2 {::0+}((BLOCKS)) Atom/(.Header.Role in (Plan))//$dependent_2;

FOR EACH $atom[<Atom>, (.Header.Role = Plan)]:
(
    IF (($atom.Header.Status = Active) AND ($atom.Header.Work Sequence Number{=1}))
    THEN ($atom.Header.Container{==1})
)
```

## Semantics

A Plan describes intended work, an intended outcome or its execution record. Work Report is the Form for that execution record.
