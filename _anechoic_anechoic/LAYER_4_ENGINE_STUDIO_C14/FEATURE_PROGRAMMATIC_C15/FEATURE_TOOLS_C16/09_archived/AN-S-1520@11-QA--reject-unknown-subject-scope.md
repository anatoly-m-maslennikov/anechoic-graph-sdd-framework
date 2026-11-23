---
atom_family: SPEC
atom_id: AN-S-1520
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Reject unknown subject scope

# Reject unknown subject scope

## Test case

**Fixture:** add one subject token outside the vocabulary registered for the carrier's structural scope.

**Expected result:** fail with the stable unknown-subject-scope diagnostic **and** a non-zero exit.
