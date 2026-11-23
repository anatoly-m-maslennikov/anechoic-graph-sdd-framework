---
atom_family: SPEC
atom_id: AN-S-210
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

Reject inverse backlink

# Reject inverse backlink

## Test case

**Fixture:** store the inverse backlink for a relation already owned by its dependent Atom.

**Expected result:** fail with the stable inverse-backlink diagnostic **and** a non-zero exit.
