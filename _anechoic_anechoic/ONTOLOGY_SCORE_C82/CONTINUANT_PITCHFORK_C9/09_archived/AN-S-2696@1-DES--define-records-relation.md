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
  version: 1
  updated_at: 2026-10-29 07:32:39 +0400
---
## Summary

Define RECORDS Relation

## Claim

RECORDS connects an Event Record to the actual occurrence described by that
record. The stored direction is Event Record to the actual Event or execution it records. IS_RECORDED_BY
is its declared derived inverse, not a second stored fact.

### Formal claim

```yaml
relation_type: RECORDS
meaning: Connect an Event Record to the actual occurrence described by that record.
derived_inverse: IS_RECORDED_BY
stored_fact: direct_only
```

## Semantics

Event Record ((RECORDS)) Workflow Run

A Workflow Run is one recorded occurrence kind, not the only one. The Event
Record persists independently of that Occurrent. This Definition imposes no
record-count constraint.

## Details

This named Type uses the general `((RELATION_TYPE))` form. It has no dedicated
short Entity operator, so `content.notation_for_subject` is intentionally
absent. This Draft creates neither a Current registration nor a runtime fact.
