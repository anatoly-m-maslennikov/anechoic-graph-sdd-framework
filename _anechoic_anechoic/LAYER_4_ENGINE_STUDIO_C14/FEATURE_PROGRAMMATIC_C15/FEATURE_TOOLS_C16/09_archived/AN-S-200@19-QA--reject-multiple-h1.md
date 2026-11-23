---
atom_family: SPEC
atom_id: AN-S-200
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:28 +0400
---
## Summary

Reject multiple H1

# Reject multiple H1

## Test case

**Fixture:** add a second body H1.

**Expected result:** fail with the stable multiple-H1 diagnostic **and** a non-zero exit.
