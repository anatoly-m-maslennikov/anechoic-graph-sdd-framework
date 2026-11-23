---
atom_family: SPEC
atom_id: AN-S-208
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Reject relation source Type

# Reject relation source Type

## Test case

**Fixture:** use a registered relation kind from a source Type it does **not** admit.

**Expected result:** fail with the stable relation-source-Type diagnostic **and** a non-zero exit.
