---
atom_family: SPEC
atom_id: AN-S-1055
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

Reject Type placement

# Reject Type placement

## Test case

**Fixture:** place a valid Requirement-prefixed carrier **in** a Content-role directory that does **not** admit Requirement.

**Expected result:** fail with the stable Type-placement diagnostic **and** a non-zero exit.
