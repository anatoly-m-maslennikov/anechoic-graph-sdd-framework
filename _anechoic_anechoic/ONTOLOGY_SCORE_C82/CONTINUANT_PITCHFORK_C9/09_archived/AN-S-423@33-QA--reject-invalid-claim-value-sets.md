---
atom_family: SPEC
atom_id: AN-S-423
container:
  component: C9
tier: 5
context:
  lens: QA
state:
  status: "archived"
  version: 33
  updated_at: "2026-11-25T22:00:01.342003+00:00"
---
## Summary

Reject Invalid Claim Value Sets

## Claim

### Prose Claim


Claim Value Sets.


the Evaluation **must** reject a Claim Value Set **if** it identifies **`!=1`** Property, has **`=0`** values, repeats a value, uses one noncanonical value, has nonfinite **or** ordered semantics, **contains** one value **not** allowed by its Property, permits one value **to** be accepted, replaced, **or** retired independently, **or** parses `:` as Subject Expression syntax.
