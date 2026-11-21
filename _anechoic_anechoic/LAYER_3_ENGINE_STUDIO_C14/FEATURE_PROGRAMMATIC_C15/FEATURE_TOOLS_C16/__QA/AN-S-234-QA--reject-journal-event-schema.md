---
atom_family: SPEC
atom_id: AN-S-234
structure:
  container:
    component: C16
  tier: 2
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject Journal event schema

# Reject Journal event schema

## Test case

**Fixture:** remove one required field from a Work Journal event.

**Expected result:** fail with the stable Journal-event-schema diagnostic **and** a non-zero exit.
