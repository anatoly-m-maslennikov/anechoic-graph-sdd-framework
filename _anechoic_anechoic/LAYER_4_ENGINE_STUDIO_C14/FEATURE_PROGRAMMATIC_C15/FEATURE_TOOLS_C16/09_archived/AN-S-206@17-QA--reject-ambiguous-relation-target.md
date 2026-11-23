---
atom_family: SPEC
atom_id: AN-S-206
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Reject ambiguous relation target

# Reject ambiguous relation target

## Test case

**Fixture:** make one relation stem resolve **to** two carriers.

**Expected result:** fail with the stable ambiguous-relation-target diagnostic **and** a non-zero exit.
