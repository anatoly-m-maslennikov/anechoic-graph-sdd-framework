---
identity:
  atom_id: AN-S-1531
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

Reject obsolete active identity

# Reject obsolete active identity

## Test case

**Fixture:** retain an obsolete framework identity **in** an active non-historical carrier **after** the governed identity migration.

**Expected result:** fail with the stable obsolete-active-identity diagnostic **and** a non-zero exit.
