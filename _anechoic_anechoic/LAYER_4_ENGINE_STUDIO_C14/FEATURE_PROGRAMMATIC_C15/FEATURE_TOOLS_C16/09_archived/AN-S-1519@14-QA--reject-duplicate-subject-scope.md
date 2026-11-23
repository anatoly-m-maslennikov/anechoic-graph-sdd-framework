---
atom_family: SPEC
atom_id: AN-S-1519
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Reject duplicate subject scope

# Reject duplicate subject scope

## Test case

**Fixture:** repeat one token **in** `subject_scopes`.

**Expected result:** fail with the stable duplicate-subject-scope diagnostic **and** a non-zero exit.
