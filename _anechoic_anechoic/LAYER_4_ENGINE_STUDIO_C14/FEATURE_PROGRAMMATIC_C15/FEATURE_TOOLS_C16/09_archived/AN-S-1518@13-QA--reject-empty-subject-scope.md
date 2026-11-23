---
atom_family: SPEC
atom_id: AN-S-1518
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Reject empty subject scope

# Reject empty subject scope

## Test case

**Fixture:** make `subject_scopes` an empty list.

**Expected result:** fail with the stable empty-subject-scope diagnostic **and** a non-zero exit.
