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
  version: 19
  updated_at: 2026-10-27 19:59:28 +0400
---
## Summary

Reject ambiguous relation target

# Reject ambiguous relation target

## Test case

**Fixture:** make one relation stem resolve **to** two carriers.

**Expected result:** fail with the stable ambiguous-relation-target diagnostic **and** a non-zero exit.
