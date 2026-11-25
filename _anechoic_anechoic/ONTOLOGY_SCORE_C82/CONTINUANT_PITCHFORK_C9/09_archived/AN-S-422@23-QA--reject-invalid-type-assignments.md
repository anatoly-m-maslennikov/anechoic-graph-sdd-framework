---
atom_family: SPEC
atom_id: AN-S-422
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-10-29 07:17:23 +0400
---
## Summary

Reject Invalid Type Assignments

# Summary

Reject Invalid Type Assignments

## Scope

Type assignments on Entity occurrences.

## Claim

the Evaluation **must** reject a Type assignment **if** **any** of the following holds:

- an Entity occurrence that bears Type has **`!=1`** direct Type values.
- the selected value is **not** allowed by its most-specific applicable qualified Type Subject.
- qualified Type Subjects create **`>1`** Type Property slots for the occurrence.

absence of a Type value **in** an Entity occurrence that does **not** bear Type is **not** a cardinality failure under this Evaluation.

## Details
