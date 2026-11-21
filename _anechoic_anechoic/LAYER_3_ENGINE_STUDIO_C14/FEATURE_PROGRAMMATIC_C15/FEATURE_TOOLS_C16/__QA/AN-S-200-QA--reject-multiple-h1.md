---
atom_family: SPEC
atom_id: AN-S-200
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

Reject multiple H1

# Reject multiple H1

## Test case

**Fixture:** add a second body H1.

**Expected result:** fail with the stable multiple-H1 diagnostic **and** a non-zero exit.
