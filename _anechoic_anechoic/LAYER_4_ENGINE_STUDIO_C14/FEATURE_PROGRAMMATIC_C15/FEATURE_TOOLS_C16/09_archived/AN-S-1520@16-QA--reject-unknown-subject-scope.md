---
atom_family: SPEC
atom_id: AN-S-1520
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 08:53:16 +0400
---
## Summary

Reject unknown subject scope

# Reject unknown subject scope

## Test case

**Fixture:** add one subject token outside the vocabulary registered for the carrier's structural scope.

**Expected result:** fail with the stable unknown-subject-scope diagnostic **and** a non-zero exit.
