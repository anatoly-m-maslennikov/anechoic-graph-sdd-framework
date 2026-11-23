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
  version: 13
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Reject same scope tier direction

# Reject same scope tier direction

## Test case

**Fixture:** **in** one structural scope, point a tier-classified RMED child at a parent with the same global tier number.

**Expected result:** fail with the stable same-scope-tier-direction diagnostic **and** a non-zero exit.
