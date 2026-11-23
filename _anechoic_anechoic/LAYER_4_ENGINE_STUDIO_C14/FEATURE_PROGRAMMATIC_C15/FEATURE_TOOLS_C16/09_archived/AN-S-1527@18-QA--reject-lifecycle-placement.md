---
atom_family: SPEC
atom_id: AN-S-1527
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reject lifecycle placement

# Reject lifecycle placement

## Test case

**Fixture:** move an active Atom into an unregistered lifecycle directory.

**Expected result:** fail with the stable lifecycle-placement diagnostic **and** a non-zero exit.
