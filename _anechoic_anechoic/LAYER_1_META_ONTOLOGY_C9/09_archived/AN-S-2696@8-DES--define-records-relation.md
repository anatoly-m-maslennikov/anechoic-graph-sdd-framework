---
atom_family: SPEC
atom_id: AN-S-2696
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Define RECORDS Relation

## Claim

### Prose Claim

RECORDS connects an Event Record to the actual occurrence described by that
record. The stored direction is Event Record to the actual Event or execution it records. IS_RECORDED_BY
is its declared derived inverse, not a second stored fact.

The Target is the actual Event or execution described by the Event Record.
Forward `Host ((RECORDS)) Target` and reverse `Target <((RECORDS)) Host` are views of the same Relation fact.
Event Record ((RECORDS)) Workflow Run

A Workflow Run is one recorded occurrence kind, not the only one. The Event
Record persists independently of that Occurrent. This Definition imposes no
record-count constraint.

#### Details
This named Type uses the general `((RELATION_TYPE))` form. It defines the reusable Type and creates no occurrence or actual endpoint tuple.
### Formal Claim

```CFEL
# model
Relation//RECORDS ((HAS_INVERSE)) Relation//IS_RECORDED_BY;

Relation//RECORDS ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Event Record//$event_record ((RECORDS)) $occurrence
```

