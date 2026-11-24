---
atom_family: SPEC
atom_id: AN-S-208
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject relation source Type

# Reject relation source Type

## Test case

**Fixture:** use a registered relation kind from a source Type it does **not** admit.

**Expected result:** fail with the stable relation-source-Type diagnostic **and** a non-zero exit.
