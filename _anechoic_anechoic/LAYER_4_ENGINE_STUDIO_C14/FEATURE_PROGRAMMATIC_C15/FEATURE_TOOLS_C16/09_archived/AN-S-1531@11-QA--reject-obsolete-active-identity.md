---
atom_family: SPEC
atom_id: AN-S-1531
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

Reject obsolete active identity

# Reject obsolete active identity

## Test case

**Fixture:** retain an obsolete framework identity **in** an active non-historical carrier **after** the governed identity migration.

**Expected result:** fail with the stable obsolete-active-identity diagnostic **and** a non-zero exit.
