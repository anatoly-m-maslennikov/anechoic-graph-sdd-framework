---
atom_family: SPEC
atom_id: AN-S-234
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Reject Journal event schema

# Reject Journal event schema

## Test case

**Fixture:** remove one required field from a Work Journal event.

**Expected result:** fail with the stable Journal-event-schema diagnostic **and** a non-zero exit.
