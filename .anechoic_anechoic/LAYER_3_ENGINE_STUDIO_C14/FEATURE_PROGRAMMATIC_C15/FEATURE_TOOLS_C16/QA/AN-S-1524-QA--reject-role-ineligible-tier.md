---
identity:
  atom_id: AN-S-1524
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

Reject role ineligible tier

# Reject role ineligible tier

## Test case

**Fixture:** give a tier-classified RMED Atom a tier unavailable **to** its Content role.

**Expected result:** fail with the stable role-ineligible-tier diagnostic **and** a non-zero exit.
