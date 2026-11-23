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
  version: 10
  updated_at: 2026-09-12 04:15:38 +0400
---
## Summary

Reject inverse backlink

# Reject inverse backlink

## Test case

**Fixture:** store the inverse backlink for a relation already owned by its dependent Atom.

**Expected result:** fail with the stable inverse-backlink diagnostic **and** a non-zero exit.
