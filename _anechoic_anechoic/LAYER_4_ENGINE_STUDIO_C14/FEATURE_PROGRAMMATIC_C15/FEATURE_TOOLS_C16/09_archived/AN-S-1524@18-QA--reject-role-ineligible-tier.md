---
atom_family: SPEC
atom_id: AN-S-1524
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reject role ineligible tier

# Reject role ineligible tier

## Test case

**Fixture:** give a tier-classified RMED Atom a tier unavailable **to** its Content role.

**Expected result:** fail with the stable role-ineligible-tier diagnostic **and** a non-zero exit.
