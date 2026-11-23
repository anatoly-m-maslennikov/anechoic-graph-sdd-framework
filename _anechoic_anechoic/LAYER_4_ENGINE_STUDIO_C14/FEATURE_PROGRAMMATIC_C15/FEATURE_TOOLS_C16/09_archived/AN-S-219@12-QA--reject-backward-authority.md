---
atom_family: SPEC
atom_id: AN-S-219
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

Reject backward authority

# Reject backward authority

## Test case

**Fixture:** point a tier-classified RMED child at an Atom **in** a descendant structural scope.

**Expected result:** fail with the stable backward-authority diagnostic **and** a non-zero exit.
