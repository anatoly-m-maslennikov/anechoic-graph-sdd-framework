---
identity:
  atom_id: AN-S-206
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

Reject ambiguous relation target

# Reject ambiguous relation target

## Test case

**Fixture:** make one relation stem resolve **to** two carriers.

**Expected result:** fail with the stable ambiguous-relation-target diagnostic **and** a non-zero exit.
