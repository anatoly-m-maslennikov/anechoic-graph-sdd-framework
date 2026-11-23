---
atom_family: SPEC
atom_id: AN-S-235
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

Reject Journal replay link

# Reject Journal replay link

## Test case

**Fixture:** point one Work Journal event at a nonexistent preceding event.

**Expected result:** fail with the stable Journal-replay-link diagnostic **and** a non-zero exit.
