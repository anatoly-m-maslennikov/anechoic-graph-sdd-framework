---
atom_family: SPEC
atom_id: AN-S-209
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

Reject relation target Type

# Reject relation target Type

## Test case

**Fixture:** use a registered relation kind toward a target Type it does **not** admit.

**Expected result:** fail with the stable relation-target-Type diagnostic **and** a non-zero exit.
