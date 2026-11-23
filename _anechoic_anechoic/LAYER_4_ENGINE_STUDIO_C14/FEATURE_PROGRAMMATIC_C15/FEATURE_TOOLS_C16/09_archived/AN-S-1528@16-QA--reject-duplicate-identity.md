---
atom_family: SPEC
atom_id: AN-S-1528
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 08:53:16 +0400
---
## Summary

Reject duplicate identity

# Reject duplicate identity

## Test case

**Fixture:** add a second active carrier with an already resolved canonical identity.

**Expected result:** fail with the stable duplicate-identity diagnostic **and** a non-zero exit.
