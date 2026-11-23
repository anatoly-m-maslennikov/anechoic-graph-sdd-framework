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
  version: 12
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reject a skipped data stage

# Reject a skipped data stage

## Test case

**Fixture:** add one generated-data dependency that skips a required registered stage.

**Expected result:** fail with the stable data-stage-direction diagnostic **and** a non-zero exit.
