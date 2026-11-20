---
atom_family: SPEC
atom_id: AN-S-213
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

Reject non direct relation

# Reject non direct relation

## Test case

**Fixture:** persist a transitive semantic edge **in** addition **to** the direct path that already entails it.

**Expected result:** fail with the stable non-direct-relation diagnostic **and** a non-zero exit.
