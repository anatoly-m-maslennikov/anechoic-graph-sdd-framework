---
identity:
  atom_id: AN-S-423
context:
  container:
    component: C00
  tier: 5
  lens: QA
state:
  status: draft
  version: 33
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Reject Invalid Claim Value Sets

## Claim

### Prose Claim


Claim Value Sets.


the Evaluation **must** reject a Claim Value Set **if** it identifies **`!=1`** Property, has **`=0`** values, repeats a value, uses one noncanonical value, has nonfinite **or** ordered semantics, **contains** one value **not** allowed by its Property, permits one value **to** be accepted, replaced, **or** retired independently, **or** parses `:` as Subject Expression syntax.
