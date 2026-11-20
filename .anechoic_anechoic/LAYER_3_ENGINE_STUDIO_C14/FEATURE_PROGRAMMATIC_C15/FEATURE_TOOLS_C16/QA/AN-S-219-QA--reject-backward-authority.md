---
identity:
  atom_id: AN-S-219
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject backward authority

# Reject backward authority

## Test case

**Fixture:** point a tier-classified RMED child at an Atom **in** a descendant structural scope.

**Expected result:** fail with the stable backward-authority diagnostic **and** a non-zero exit.
