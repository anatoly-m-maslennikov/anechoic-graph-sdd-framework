---
atom_family: SPEC
atom_id: AN-S-235
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Reject Journal replay link

# Reject Journal replay link

## Test case

**Fixture:** point one Work Journal event at a nonexistent preceding event.

**Expected result:** fail with the stable Journal-replay-link diagnostic **and** a non-zero exit.
