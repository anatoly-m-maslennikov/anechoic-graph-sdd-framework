---
atom_family: SPEC
atom_id: AN-S-1730
structure:
  container:
    component: C9
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 33
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Validate Atom replacement event evidence

## Claim

### Prose Claim


Atom replacement event evidence.


an Event Record offered as Atom replacement evidence **must** undergo an actual Evaluation against CA-R-807. Available evidence and Journal acceptance are **not** proof that the replacement is correct.

## Details

### Checks

the Evaluation of that Event Record **must** run and report a passing, failed, or unresolved result. It **must**:

- report a failed replacement result **if** predecessor **or** successor identities are missing, unresolved, duplicate, self-referencing, **or** mismatched;
- verify that **every** named successor was Active **before** the predecessor was archived, that the archived predecessor preserves its body, Summary, identity, numeric Version, and prior Updated At, with only archived Status changed on its Archive Carrier; verify retained exact prior Revision bytes, including the prior Version, Status **and** Updated At, and that **`=1`** authoritative Journal Event Record records that replacement;
- distinguish selected Carrier representation evidence from proof of replacement correctness; and
- treat repeated submission of the same Event Record as non-evidence of another authoritative record.

### Failure disposition

an Event Record whose actual Evaluation reports failure **or** uncertainty **must not** be treated as a conforming replacement merely because the Journal preserves it under CA-R-1491. Its correction disposition **must** route a governed-source change through its authorized Workflow and **must not** rewrite accepted history.

this Evaluation **must not** require a Git Commit **or** a particular Journal serialization. Available evidence without the performed Evaluation and its reported result is **not** a passing result.
