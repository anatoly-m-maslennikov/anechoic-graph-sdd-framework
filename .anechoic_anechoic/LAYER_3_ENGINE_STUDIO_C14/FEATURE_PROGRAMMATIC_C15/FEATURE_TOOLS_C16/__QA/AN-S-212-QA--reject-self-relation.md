---
atom_family: SPEC
atom_id: AN-S-212
structure:
  container:
    component: C16
  tier: 2
context:
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-10-27 19:59:28 +0400
---
## Summary

Reject self relation

# Reject self relation

## Test case

**Fixture:** point an active normative-authority `child_of` Relation from an Atom **to** itself under CA-R-879. this self-edge creates a cycle prohibited by CA-R-833; do **not** infer a universal self-edge prohibition for other graph kinds **or** Relation Kinds.

**Expected result:** fail with the stable self-relation diagnostic **and** a non-zero exit.
