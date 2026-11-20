---
identity:
  atom_id: AN-S-209
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

Reject relation target Type

# Reject relation target Type

## Test case

**Fixture:** use a registered relation kind toward a target Type it does **not** admit.

**Expected result:** fail with the stable relation-target-Type diagnostic **and** a non-zero exit.
