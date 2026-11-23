---
atom_family: SPEC
atom_id: AN-S-200
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-09-12 04:15:38 +0400
---
## Summary

Reject multiple H1

# Reject multiple H1

## Test case

**Fixture:** add a second body H1.

**Expected result:** fail with the stable multiple-H1 diagnostic **and** a non-zero exit.
