---
identity:
  atom_id: AN-S-245
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 21
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject an unresolved configuration proof revision

# Reject an unresolved configuration proof revision

## Test case

**Fixture:** leave one required configuration revision unresolved **in** a proof frontier.

**Expected result:** fail with the stable incomplete-proof-frontier diagnostic **and** a non-zero exit.
