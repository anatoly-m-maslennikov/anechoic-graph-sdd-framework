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
  version: 19
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Reject unknown Type prefix

# Reject unknown Type prefix

## Test case

**Fixture:** replace the filename Type prefix with an unregistered four-character prefix.

**Expected result:** fail with the stable unknown-Type-prefix diagnostic **and** a non-zero exit.
