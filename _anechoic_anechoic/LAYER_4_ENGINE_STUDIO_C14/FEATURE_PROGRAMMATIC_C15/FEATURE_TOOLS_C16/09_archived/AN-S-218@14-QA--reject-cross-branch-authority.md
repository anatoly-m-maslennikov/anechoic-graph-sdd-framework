---
atom_family: SPEC
atom_id: AN-S-218
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

Reject cross branch authority

# Reject cross branch authority

## Test case

**Fixture:** point a tier-classified RMED child at a same-tier Atom **in** a sibling structural scope.

**Expected result:** fail with the stable cross-branch-authority diagnostic **and** a non-zero exit.
