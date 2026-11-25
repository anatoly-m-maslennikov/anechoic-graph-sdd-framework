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
  version: 36
  updated_at: "2026-11-25T22:00:01.414310+00:00"
---
## Summary

Validate Atom replacement event evidence

## Claim

### Prose Claim


Atom replacement event evidence.


When an Event Record is offered as replacement evidence, verify the actual source effects under AN-S-1846.

## Details

### Checks

the Evaluation of that Event Record **must** run and report a passing, failed, or unresolved result. It **must**:

- report a failed replacement result **if** predecessor **or** successor identities are missing, unresolved, duplicate, self-referencing, **or** mismatched;
- verify that the applicable predecessor was Archived before the successor was published. Check its archived identity, Version, preserved content, and edit time. Compare the Event Record identities with the verified effects;
- distinguish selected Carrier representation evidence from proof of replacement correctness; and
- treat repeated submission of the same Event Record as non-evidence of another authoritative record.

### Failure disposition

an Event Record whose actual Evaluation reports failure **or** uncertainty **must not** be treated as a conforming replacement merely because the Journal preserves it under CA-R-1491. Its correction disposition **must** route a governed-source change through its authorized Workflow and **must not** rewrite accepted history.

this Evaluation **must not** require a Git Commit **or** a particular Journal serialization. Available evidence without the performed Evaluation and its reported result is **not** a passing result.
