---
atom_family: SPEC
atom_id: AN-S-1074
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

Reject a skipped data stage

# Reject a skipped data stage

## Test case

**Fixture:** add one generated-data dependency that skips a required registered stage.

**Expected result:** fail with the stable data-stage-direction diagnostic **and** a non-zero exit.
