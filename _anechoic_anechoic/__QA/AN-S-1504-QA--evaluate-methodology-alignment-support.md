---
atom_family: SPEC
atom_id: AN-S-1504
container:
  component: C00
tier: 5
context:
  lens: QA
state:
  status: active
  version: 27
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary
Evaluate methodology alignment support

## Claim

### Prose Claim


the methodology alignment support Evaluation **must** return `fail` **if** the available Tools cannot assess the governed instance against the current Applicable Methodology, omit known nonconformance, cannot support an authorized repair, **or** mutate authority **without** Operator permission; a targeted check **may** use a bounded affected Scope **and** its dependencies. an unresolved finding **or** Operator-created orphan **must not** by itself establish failure of the required support capability **or** be reported as conformance.
