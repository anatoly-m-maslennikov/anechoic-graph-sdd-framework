---
atom_family: SPEC
atom_id: AN-S-220
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Reject authority cycle

# Reject authority cycle

## Test case

**Fixture:** add one `child_of` edge that closes a cycle.

**Expected result:** fail with the stable authority-cycle diagnostic **and** a non-zero exit.
