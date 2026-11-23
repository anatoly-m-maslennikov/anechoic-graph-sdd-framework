---
atom_family: SPEC
atom_id: AN-S-1062
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Propagate Atom filename diagnostics

# Propagate Atom filename diagnostics

## Test case

**Fixture:** add one carrier that fails the malformed-filename fixture defined by CA-E-073 while leaving the rest of the project valid.

**Expected result:** fail with the propagated malformed-filename diagnostic **and** a non-zero exit.
