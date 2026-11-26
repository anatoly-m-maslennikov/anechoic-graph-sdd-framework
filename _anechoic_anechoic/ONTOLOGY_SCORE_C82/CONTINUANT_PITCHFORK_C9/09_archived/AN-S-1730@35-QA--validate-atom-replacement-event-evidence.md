---
atom_family: SPEC
atom_id: AN-S-1730
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: "archived"
  version: 35
  updated_at: "2026-11-25T19:50:48.162024+00:00"
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
- verify that the predecessor was Archived before any named successor became Active, that the archived predecessor preserves its body, Summary, identity, numeric Version, with Archived Status and Updated At set on the Archive Carrier; verify retained exact prior Revision bytes, including the prior Version, Status **and** Updated At, and that **`=1`** authoritative Journal Event Record records that replacement;
- distinguish selected Carrier representation evidence from proof of replacement correctness; and
- treat repeated submission of the same Event Record as non-evidence of another authoritative record.

### Failure disposition

an Event Record whose actual Evaluation reports failure **or** uncertainty **must not** be treated as a conforming replacement merely because the Journal preserves it under CA-R-1491. Its correction disposition **must** route a governed-source change through its authorized Workflow and **must not** rewrite accepted history.

this Evaluation **must not** require a Git Commit **or** a particular Journal serialization. Available evidence without the performed Evaluation and its reported result is **not** a passing result.
