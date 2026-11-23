---
atom_family: SPEC
atom_id: AN-S-1068
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

Reject a backward data-stage dependency

# Reject a backward data-stage dependency

## Test case

**Fixture:** add one generated-data dependency that moves backward.

**Expected result:** fail with the stable data-stage-direction diagnostic **and** a non-zero exit.
