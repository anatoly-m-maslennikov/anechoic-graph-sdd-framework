---
atom_family: SPEC
atom_id: AN-S-1055
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

Reject Type placement

# Reject Type placement

## Test case

**Fixture:** place a valid Requirement-prefixed carrier **in** a Content-role directory that does **not** admit Requirement.

**Expected result:** fail with the stable Type-placement diagnostic **and** a non-zero exit.
