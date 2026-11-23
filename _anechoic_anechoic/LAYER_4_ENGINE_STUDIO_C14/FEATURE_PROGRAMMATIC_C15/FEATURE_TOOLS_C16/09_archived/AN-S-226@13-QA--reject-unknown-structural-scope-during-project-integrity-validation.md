---
atom_family: SPEC
atom_id: AN-S-226
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-23 03:18:40 +0400
---
## Summary

Reject unknown structural scope during project integrity validation

# Reject unknown structural scope during project integrity validation

## Test case

**Fixture:** include CA-E-076's undeclared non-Project Scope Unit Carrier fixture **in** an otherwise conforming Project. resolve Scope Unit declarations from authoritative Project Structure, **not** arbitrary directory names; a Content Role folder, lifecycle folder, **or** Atom Collection **must not** become a Scope Unit merely because it is a folder.

**Expected result:** propagate the stable unknown-structural-scope diagnostic for the undeclared Scope Unit fixture with a non-zero exit. do **not** apply that diagnostic **to** an admitted non-Scope-Unit directory solely because it lacks a Scope Unit declaration.
