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
  version: 10
  updated_at: 2026-09-12 04:15:38 +0400
---
## Summary

Reject empty subject scope

# Reject empty subject scope

## Test case

**Fixture:** make `subject_scopes` an empty list.

**Expected result:** fail with the stable empty-subject-scope diagnostic **and** a non-zero exit.
