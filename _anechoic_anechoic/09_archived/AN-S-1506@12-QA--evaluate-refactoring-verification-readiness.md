---
atom_family: SPEC
atom_id: AN-S-1506
container:
  component: C00
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Evaluate refactoring verification readiness

# Evaluate refactoring verification readiness

the refactoring-verification Evaluation **must** return `fail` **if**

- the target Implementation changes **before** applicable verification is prepared **and** the existing Implementation baseline is recorded,
- baseline inputs are incomplete **or** uncontrolled,
- an existing defect becomes expected correctness **without** governing authority,
- the candidate is **not** checked against the governing RMED **and** baseline,
- **or** required release gates are bypassed.

**when** canary testing applies, it **must** return `fail` **if**

- criteria were **not** prepared **before** refactoring
- **or** the canary is reported as executed **without** running the candidate during an authorized controlled rollout.

absence of an inapplicable testing technique **or** of an old-Implementation baseline for a fresh reconstruction **must not** by itself cause failure. baseline observations **must not** replace RMED as authority.
