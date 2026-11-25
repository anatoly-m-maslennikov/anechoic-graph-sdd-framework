---
atom_family: SPEC
atom_id: AN-S-1505
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 31
  updated_at: "2026-11-25T22:00:01.688603+00:00"
---
## Summary
Evaluate implementation mode conformance

## Claim

### Prose Claim


the implementation mode Evaluation **must** return `fail` **if**

- execution replaces the Operator-selected mode **without** authorization,
- treats an evaluation-and-fix request as permission for a full rebuild,
- exceeds Task permissions,
- **or** exempts the selected mode from the governing RMED.

authorized rewriting **or** different source-code bytes **must not** by themselves cause failure **when** reconstruction equivalence under CA-M-262 is preserved.
