---
atom_family: SPEC
atom_id: AN-S-1074
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

Reject a skipped data stage

# Reject a skipped data stage

## Test case

**Fixture:** add one generated-data dependency that skips a required registered stage.

**Expected result:** fail with the stable data-stage-direction diagnostic **and** a non-zero exit.
