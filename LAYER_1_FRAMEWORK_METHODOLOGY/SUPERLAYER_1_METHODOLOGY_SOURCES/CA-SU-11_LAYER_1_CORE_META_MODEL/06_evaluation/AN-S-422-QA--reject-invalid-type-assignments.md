---
identity:
  atom_id: AN-S-422
context:
  container:
    component: C9
  tier: 3
  lens: QA
state:
  status: active
  version: 27
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Reject Invalid Type Assignments

## Claim

### Prose Claim


Type assignments on Entity occurrences.


the Evaluation **must** reject a Type assignment **if** **any** of the following holds:

- an Entity occurrence that bears Type has **`!=1`** direct Type values.
- the selected value is **not** allowed by its most-specific applicable qualified Type Subject.
- qualified Type Subjects create **`>1`** Type Property slots for the occurrence.

absence of a Type value **in** an Entity occurrence that does **not** bear Type is **not** a cardinality failure under this Evaluation.
