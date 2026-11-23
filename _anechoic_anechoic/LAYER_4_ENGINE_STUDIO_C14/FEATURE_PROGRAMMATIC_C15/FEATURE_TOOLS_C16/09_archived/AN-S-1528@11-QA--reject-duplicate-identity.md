---
atom_family: SPEC
atom_id: AN-S-1528
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Reject duplicate identity

# Reject duplicate identity

## Test case

**Fixture:** add a second active carrier with an already resolved canonical identity.

**Expected result:** fail with the stable duplicate-identity diagnostic **and** a non-zero exit.
