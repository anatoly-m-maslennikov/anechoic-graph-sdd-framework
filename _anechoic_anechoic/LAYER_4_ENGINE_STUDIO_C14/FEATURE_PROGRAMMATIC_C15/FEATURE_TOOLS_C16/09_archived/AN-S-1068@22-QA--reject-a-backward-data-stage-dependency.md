---
atom_family: SPEC
atom_id: AN-S-1068
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject a backward data-stage dependency

# Reject a backward data-stage dependency

## Test case

**Fixture:** add one generated-data dependency that moves backward.

**Expected result:** fail with the stable data-stage-direction diagnostic **and** a non-zero exit.
