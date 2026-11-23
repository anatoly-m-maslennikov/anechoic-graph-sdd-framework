---
atom_family: SPEC
atom_id: AN-S-1522
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Reject numeric tier

# Reject numeric tier

## Test case

**Fixture:** give a tier-classified RMED Atom a numeric `tier`.

**Expected result:** fail with the stable numeric-tier diagnostic **and** a non-zero exit.
