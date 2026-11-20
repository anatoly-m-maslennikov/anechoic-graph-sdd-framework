---
identity:
  atom_id: AN-S-1505
context:
  container:
    component: C00
  tier: 3
  lens: QA
state:
  status: draft
  version: 26
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary
Evaluate implementation mode conformance

## Claim

the implementation mode Evaluation **must** return `fail` **if**

- execution replaces the Operator-selected mode **without** authorization,
- treats an evaluation-and-fix request as permission for a full rebuild,
- exceeds Task permissions,
- **or** exempts the selected mode from the governing RMED.

authorized rewriting **or** different source-code bytes **must not** by themselves cause failure **when** reconstruction equivalence under CA-M-262 is preserved.
