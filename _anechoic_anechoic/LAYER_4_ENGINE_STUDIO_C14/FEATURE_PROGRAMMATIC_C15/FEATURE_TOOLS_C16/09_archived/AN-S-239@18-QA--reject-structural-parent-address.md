---
atom_family: SPEC
atom_id: AN-S-239
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Reject structural parent address

# Reject structural parent address

## Test case

**Fixture:** give a Scope Unit using the default directory convention a directory address inconsistent with its declared parent. include an explicit native binding admitted by CA-D-445 as a control, with different physical nesting **or** numeric tokens but unchanged declared parentage **and** Structural Level.

**Expected result:** fail the default-convention mismatch with the stable structural-parent-address diagnostic **and** a non-zero exit. do **not** reject the admitted native control for its physical topology alone; retain its boundary, ownership, uniqueness **and** explicit-binding checks. do **not** derive a new structural declaration from either path.
