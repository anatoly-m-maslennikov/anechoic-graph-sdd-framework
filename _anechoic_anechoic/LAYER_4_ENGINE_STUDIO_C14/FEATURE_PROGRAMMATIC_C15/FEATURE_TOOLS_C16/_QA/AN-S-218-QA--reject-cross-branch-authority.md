---
atom_family: SPEC
atom_id: AN-S-218
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject cross branch authority

# Reject cross branch authority

## Test case

**Fixture:** point a tier-classified RMED child at a same-tier Atom **in** a sibling structural scope.

**Expected result:** fail with the stable cross-branch-authority diagnostic **and** a non-zero exit.
