---
atom_family: SPEC
atom_id: AN-S-210
structure:
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

Reject inverse backlink

# Reject inverse backlink

## Test case

**Fixture:** store the inverse backlink for a relation already owned by its dependent Atom.

**Expected result:** fail with the stable inverse-backlink diagnostic **and** a non-zero exit.
