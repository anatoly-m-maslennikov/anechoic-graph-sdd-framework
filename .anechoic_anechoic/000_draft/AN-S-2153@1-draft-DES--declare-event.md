---
atom_family: SPEC
atom_id: AN-S-2153
structure:
  container:
    component: C00
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-04 16:07:35 +0400
---

## Summary

Declare Event

## Claim

### Formal Claim

```CFEL
# model
Event ((NARROWER_THAN)) Occurrent;

# instances
Event//$event {::0+}((IS_RECORDED_BY)) Event Record//$record;

Event//$produced_event {::1+}((IS_PRODUCED_BY)) Execution//$producer
```

## Semantics

An Event is an occurrence produced by an Execution.
