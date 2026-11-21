---
atom_family: SPEC
atom_id: AN-S-1519
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject duplicate subject scope

# Reject duplicate subject scope

## Test case

**Fixture:** repeat one token **in** `subject_scopes`.

**Expected result:** fail with the stable duplicate-subject-scope diagnostic **and** a non-zero exit.
