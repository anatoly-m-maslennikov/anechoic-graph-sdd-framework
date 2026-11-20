---
atom_family: SPEC
atom_id: AN-S-1062
structure:
  container:
    component: C16
  tier: 2
context:
  lens: QA
state:
  status: active
  version: 23
  updated_at: 2026-10-27 19:59:28 +0400
---
## Summary

Propagate Atom filename diagnostics

# Propagate Atom filename diagnostics

## Test case

**Fixture:** add one carrier that fails the malformed-filename fixture defined by CA-E-073 while leaving the rest of the project valid.

**Expected result:** fail with the propagated malformed-filename diagnostic **and** a non-zero exit.
