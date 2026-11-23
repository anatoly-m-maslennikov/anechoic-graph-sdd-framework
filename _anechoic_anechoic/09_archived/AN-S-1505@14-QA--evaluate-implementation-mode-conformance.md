---
atom_family: SPEC
atom_id: AN-S-1505
container:
  component: C00
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 10:35:14 +0400
---
## Summary

Evaluate implementation mode conformance

# Evaluate implementation mode conformance

the implementation mode Evaluation **must** return `fail` **if**

- execution replaces the Operator-selected mode **without** authorization,
- treats an evaluation-and-fix request as permission for a full rebuild,
- exceeds Task permissions,
- **or** exempts the selected mode from the governing RMED.

authorized rewriting **or** different source-code bytes **must not** by themselves cause failure **when** reconstruction equivalence under CA-M-262 is preserved.
