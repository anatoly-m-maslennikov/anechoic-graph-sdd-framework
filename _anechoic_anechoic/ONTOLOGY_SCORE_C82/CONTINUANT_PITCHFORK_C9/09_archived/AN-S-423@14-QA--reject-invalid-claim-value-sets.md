---
atom_family: SPEC
atom_id: AN-S-423
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-22 16:18:21 +0000
---
## Summary

Reject Invalid Claim Value Sets

# Summary

Reject Invalid Claim Value Sets

## Scope

Claim Value Sets.

## Claim

the Evaluation **must** reject a Claim Value Set **if** it identifies **`!=1`** Property, has **`=0`** values, repeats a value, uses one noncanonical value, has nonfinite **or** ordered semantics, **contains** one value **not** allowed by its Property, permits one value **to** be accepted, replaced, **or** retired independently, **or** parses `:` as Subject Expression syntax.

## Details
