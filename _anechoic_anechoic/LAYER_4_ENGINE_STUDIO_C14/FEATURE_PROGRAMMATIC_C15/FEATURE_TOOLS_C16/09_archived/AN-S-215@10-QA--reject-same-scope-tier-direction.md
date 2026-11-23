---
atom_family: SPEC
atom_id: AN-S-215
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-09-12 04:15:38 +0400
---
## Summary

Reject same scope tier direction

# Reject same scope tier direction

## Test case

**Fixture:** **in** one structural scope, point a tier-classified RMED child at a parent with the same global tier number.

**Expected result:** fail with the stable same-scope-tier-direction diagnostic **and** a non-zero exit.
