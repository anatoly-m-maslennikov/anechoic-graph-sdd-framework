---
identity:
  atom_id: AN-S-220
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 25
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject authority cycle

# Reject authority cycle

## Test case

**Fixture:** add one `child_of` edge that closes a cycle.

**Expected result:** fail with the stable authority-cycle diagnostic **and** a non-zero exit.
