---
identity:
  atom_id: AN-S-201
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject summary H1 mismatch

# Reject summary H1 mismatch

## Test case

**Fixture:** change the H1 so it no longer faithfully renders the immutable filename summary.

**Expected result:** fail with the stable summary-H1-mismatch diagnostic **and** a non-zero exit.
