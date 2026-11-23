---
atom_family: SPEC
atom_id: AN-S-234
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Reject Journal event schema

# Reject Journal event schema

## Test case

**Fixture:** remove one required field from a Work Journal event.

**Expected result:** fail with the stable Journal-event-schema diagnostic **and** a non-zero exit.
