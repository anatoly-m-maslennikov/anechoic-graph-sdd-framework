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
  version: 14
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Reject duplicate identity

# Reject duplicate identity

## Test case

**Fixture:** add a second active carrier with an already resolved canonical identity.

**Expected result:** fail with the stable duplicate-identity diagnostic **and** a non-zero exit.
