---
identity:
  atom_id: AN-S-1054
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject unknown Type prefix

# Reject unknown Type prefix

## Test case

**Fixture:** replace the filename Type prefix with an unregistered four-character prefix.

**Expected result:** fail with the stable unknown-Type-prefix diagnostic **and** a non-zero exit.
