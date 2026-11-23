---
atom_family: SPEC
atom_id: AN-S-1054
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-27 19:59:28 +0400
---
## Summary

Reject unknown Type prefix

# Reject unknown Type prefix

## Test case

**Fixture:** replace the filename Type prefix with an unregistered four-character prefix.

**Expected result:** fail with the stable unknown-Type-prefix diagnostic **and** a non-zero exit.
