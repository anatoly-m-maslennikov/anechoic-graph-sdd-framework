---
atom_family: SPEC
atom_id: AN-S-215
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

Reject same scope tier direction

# Reject same scope tier direction

## Test case

**Fixture:** **in** one structural scope, point a tier-classified RMED child at a parent with the same global tier number.

**Expected result:** fail with the stable same-scope-tier-direction diagnostic **and** a non-zero exit.
